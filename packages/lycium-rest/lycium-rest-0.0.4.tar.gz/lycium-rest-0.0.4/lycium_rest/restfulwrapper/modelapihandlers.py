#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import tornado.web
import tornado.httputil
import tornado.gen
import asyncio
import sqlalchemy
import i18n
import json
import traceback
from http import HTTPStatus
from typing import Iterable
from wtforms import Form
from hawthorn.asynchttphandler import GeneralTornadoHandler, request_body_as_json, routes
from hawthorn.session import TornadoSession
from hawthorn.exceptionreporter import ExceptionReporter
from hawthorn.modelutils import ModelBase, model_columns, get_model_class_name
from hawthorn.dbproxy import DbProxy
from hawthorn.utilities import pascal_case
from ..utilities.treedata import format_items_as_tree
from . import SESSION_UID_KEY
from ..formvalidation.formutils import validate_form, save_form_fields
from ..valueobjects.resultcodes import RESULT_CODE
from ..valueobjects.responseobject import GeneralResponseObject, ListResponseObject

from .utils import format_model_query_conditions, format_column_name_mappings, dump_model_data, read_request_parameters, get_locale_params, get_listquery_pager_info, get_listquery_sort_info, get_listquery_filters_and_specified_fields

LOG = logging.getLogger('services.generalmodelapi.apihandlers')

class ModelRESTfulHandler(tornado.web.RequestHandler):
    """
    Model API handler wrapper
    """
    def initialize(self, model: ModelBase, form: Form = None, ac=[], auto_association: str|list[str]=None):
        self.model = model
        self.form = form
        self._ac = []
        self.session = TornadoSession(self)
        self.set_access_control(ac)
        self.find_one_keys = {'fetchOne': True, 'findOne': True}
        self.auto_association_keys = {}
        if auto_association:
            if isinstance(auto_association, str):
                self.auto_association_keys['fetchTree'] = auto_association
            elif isinstance(auto_association, list):
                if len(auto_association) == 1:
                    self.auto_association_keys['fetchTree'] = auto_association[0]
                else:
                    for k in auto_association:
                        self.auto_association_keys['fetchTreeBy' + pascal_case(k)] = k

    def set_access_control(self, ac):
        self._ac = []
        if ac:
            if isinstance(ac, list):
                for f in ac:
                    if callable(f):
                        self._ac.append(['', f])
            elif isinstance(ac, dict):
                for k, f in ac:
                    if callable(f):
                        self._ac.append([k, f])
            elif callable(ac):
                self._ac.append(['', ac])
                
    async def check_access_control(self):
        is_reject = False
        reject_reason = ''
        for o in self._ac:
            f = o[1]
            try:
                if tornado.gen.is_coroutine_function(f) or asyncio.iscoroutinefunction(f):
                    ac_result, msg = await f(self)
                else:
                    ac_result, msg = f(self)
            except Exception as e:
                LOG.warning('verify %s access control %s excepted with error:%s traceback:%s', self.request.path, str(o[0]), str(e), traceback.format_exc())
                ac_result = False
                msg = str(e)
                ExceptionReporter().report(key='ACL-' + self.request.path, typ='HTTP', 
                    endpoint=self.request.path,
                    method=self.request.method,
                    inputs=str(o[0]),
                    outputs='',
                    content=str(e),
                    level='ERROR'
                )
            if not ac_result:
                reject_reason = str(msg)
                LOG.warning('verify %s access control %s failed with error:%s', self.request.path, str(o[0]), reject_reason)
                is_reject = True
                break
        return is_reject, reject_reason
    
    def set_default_headers(self):
        """Responses default headers"""
        if routes.default_headers:
            for k, v in routes.default_headers.items():
                self.set_header(k, v)

    async def prepare(self):
        is_reject, reject_reason = await self.check_access_control()
        if is_reject:
            self.write(reject_reason)
            self.set_status(HTTPStatus.FORBIDDEN)
            self.finish()
            return

    async def get(self, id: str|int = None):
        """
        API handler of get single model data
        """
        filters = read_request_parameters(self.request)
        locale_params = get_locale_params(self.request)
        if id:
            if id in self.auto_association_keys:
                result = await self.do_get_tree_list(id, filters, locale_params)
            else:
                columns, pk = model_columns(self.model)
                if id not in self.find_one_keys:
                    filters[pk] = id
                result = GeneralResponseObject(RESULT_CODE.DATA_DOES_NOT_EXISTS, message=i18n.t('basic.data_not_exists', **locale_params))
                while result.code != RESULT_CODE.OK:
                    filter_conds, err_msg = format_model_query_conditions(self.model, filters=filters)
                    if err_msg:
                        result.code = RESULT_CODE.INVALID_PARAM
                        result.message = err_msg
                        break

                    m = await DbProxy().find_item(self.model, filters=filter_conds)
                    if m:
                        result.code = RESULT_CODE.OK
                        result.message = i18n.t('basic.success', **locale_params)
                        if hasattr(m, 'as_dict'):
                            result.data = getattr(m, 'as_dict')()
                        else:
                            result.data = dump_model_data(m, columns=columns, column_name_mapping=format_column_name_mappings(self.form))
                    break
        else:
            result = await self.do_get_list(filters, locale_params)
        
        self.set_header('Content-Type', 'application/json')
        self.write(result.encode_json())
        self.finish()

    async def post(self, id: str|int = None):
        """
        API handler of add model instance data
        """
        if id:
            self.set_status(HTTPStatus.NOT_FOUND)
            self.finish()
            return
        locale_params = get_locale_params(self.request)
        if not self.form:
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR, '%s form not configured for general form handler, please specify form when register model general api handlers' % (get_model_class_name(self.model)))
            self.finish()
            return
        inputs = request_body_as_json(self.request)
        if not inputs:
            self.set_status(HTTPStatus.NO_CONTENT, i18n.t('basic.invalid_param', **locale_params))
            self.finish()
            return
        form_items = []
        if isinstance(inputs, list):
            for ele in inputs:
                form_items.append(self.form(formdata=None, data=ele, meta={'csrf': False}))
        else:
            form_items.append(self.form(formdata=None, data=inputs, meta={'csrf': False}))
            
        insert_models = []
        after_saves = []
        for form_item in form_items:
            result = validate_form(form_item)
            if not result.is_success():
                self.set_header('Content-Type', 'application/json')
                self.write(result.encode_json())
                self.finish()
                return

            m = self.model()
            if hasattr(m, 'set_session_uid'):
                session_uid = self.session[SESSION_UID_KEY]
                setattr(m, 'set_session_uid', session_uid)
                
            b, msg = await self._check_before_save(form_item)
            if not b:
                result.code = RESULT_CODE.INVALID_PARAM
                result.message = msg
                self.set_header('Content-Type', 'application/json')
                self.write(result.encode_json())
                self.finish()
                return
            if hasattr(form_item, 'after_save'):
                after_saves.append(getattr(form_item, 'after_save'))
                
            save_form_fields(form_item, m, ignore_empty=True)
            insert_models.append(m)

        result = GeneralResponseObject(code=RESULT_CODE.FAIL, message=i18n.t('basic.create_data_failed', **locale_params))
        
        # m = self.model()
        # if hasattr(m, 'set_session_uid'):
        #     session_uid = self.session[SESSION_UID_KEY]
        #     setattr(m, 'set_session_uid', session_uid)
        # save_form_fields(form_item, m, ignore_empty=True)

        try:
            res = await DbProxy().insert_items(insert_models, auto_flush=True)
            if res:
                result.code = RESULT_CODE.OK
                result.message = i18n.t('basic.success', **locale_params)
                resp_data = []
                for m in insert_models:
                    if hasattr(m, 'as_dict'):
                        resp_data.append(getattr(m, 'as_dict')())
                    else:
                        resp_data.append(dump_model_data(m))
                if isinstance(inputs, list):
                    result.data = resp_data
                else:
                    result.data = resp_data[0]
                LOG.info('insert [%s] succeed', get_model_class_name(self.model))
                if after_saves:
                    i = 0
                    for cb in after_saves:
                        await self._call(cb, session=self.session, data=insert_models[i])
                        i = i + 1
            else:
                LOG.warning('insert [%s] failed', get_model_class_name(self.model))
        except Exception as e:
            LOG.error('insert [%s] failed with error:%s', get_model_class_name(self.model), str(e))
            result.code = RESULT_CODE.FAIL
            result.message = str(e)
        
        self.set_header('Content-Type', 'application/json')
        self.write(result.encode_json())
        self.finish()
    
    async def put(self, id: str|int = None):
        if not id:
            self.set_status(HTTPStatus.NOT_FOUND)
            self.finish()
            return
        await self.do_edit(id, True)
    
    async def patch(self, id: str|int = None):
        if not id:
            self.set_status(HTTPStatus.NOT_FOUND)
            self.finish()
            return
        await self.do_edit(id, False)

    async def delete(self, id: str|int = None):
        """
        API handler of delete model instance data
        """
        if not id:
            self.set_status(HTTPStatus.NOT_FOUND)
            self.finish()
            return
        # inputs = request_body_as_json(self.request)
        locale_params = get_locale_params(self.request)
        columns, pk = model_columns(self.model)
        form_pk_id = id
        if not form_pk_id:
            LOG.warning('delete %s while not giving any id to delete', get_model_class_name(self.model))
            return GeneralResponseObject(code=RESULT_CODE.INVALID_PARAM, message=i18n.t('basic.invalid_param', **locale_params)).encode_json()
        m = await DbProxy().find_item(self.model, {getattr(self.model, pk)==form_pk_id})
        if not m:
            LOG.warning('delete %s [%s] info failed while data does not extsts', get_model_class_name(self.model), str(form_pk_id))
            return GeneralResponseObject(code=RESULT_CODE.DATA_DOES_NOT_EXISTS, message=i18n.t('basic.data_not_exists', **locale_params)).encode_json()
        
        result = GeneralResponseObject(code=RESULT_CODE.FAIL, message=i18n.t('basic.delete_data_failed', **locale_params))
        try:
            res = False
            if False and hasattr(m, 'obsoleted'):
                if hasattr(m, 'set_session_uid'):
                    session_uid = self.session[SESSION_UID_KEY]
                    setattr(m, 'set_session_uid', session_uid)
                setattr(m, 'obsoleted', 1)
                res = await DbProxy().update_item(m)
            else:
                res = await DbProxy().del_item(m)
            if res:
                result.code = RESULT_CODE.OK
                result.message = i18n.t('basic.success', **locale_params)
                LOG.info('delete %s [%s] succeed', get_model_class_name(self.model), str(form_pk_id))
            else:
                LOG.warning('delete %s [%s] failed', get_model_class_name(self.model), str(form_pk_id))
        except Exception as e:
            LOG.error('delete %s [%s] failed with error:%s', get_model_class_name(self.model), str(form_pk_id), str(e))
            result.code = RESULT_CODE.FAIL
            result.message = str(e)

        self.set_header('Content-Type', 'application/json')
        self.write(result.encode_json())
        self.finish()

    async def do_get_list(self, params: dict, locale_params: dict):
        """
        API handler of get model list data by filter condition and pagination
        """
        filters, fields = get_listquery_filters_and_specified_fields(params)
        limit, offset = get_listquery_pager_info(params)
        orderby, direction = get_listquery_sort_info(params)

        result = ListResponseObject(RESULT_CODE.DATA_DOES_NOT_EXISTS, message=i18n.t('basic.data_not_exists', **locale_params))
        while result.code != RESULT_CODE.OK:
            filter_conds, err_msg = format_model_query_conditions(self.model, filters=filters)
            if err_msg:
                result.code = RESULT_CODE.INVALID_PARAM
                result.message = err_msg
                break

            rows, total = await DbProxy().query_list(self.model, filters=filter_conds, limit=limit, offset=offset, sort=orderby, direction=direction, selections=fields)
            
            if not fields and hasattr(self.model, 'as_dict'):
                formatted_rows = []
                for row in rows:
                    m = self.model()
                    for k, v in row.items():
                        setattr(m, k, v)
                    formatted_rows.append(getattr(m, 'as_dict')())
                rows = formatted_rows
            else:
                column_name_mapping = format_column_name_mappings(self.form)
                if column_name_mapping:
                    rows = [{column_name_mapping.get(k, k): v for k, v in row.items()} for row in rows]

            result.code = RESULT_CODE.OK
            result.message = i18n.t('basic.success', **locale_params)
            result.total = total
            result.data = rows
            if limit:
                result.pageSize = limit
                result.page = int(offset/limit) + 1
        return result

    async def do_get_tree_list(self, id: str, params: dict, locale_params: dict):
        """
        API handler of get model tree list data by filter condition
        """
        filters, fields = get_listquery_filters_and_specified_fields(params)
        limit, offset = get_listquery_pager_info(params, default_list_limit=3000, max_list_limit=5000)
        orderby, direction = get_listquery_sort_info(params)

        result = ListResponseObject(RESULT_CODE.DATA_DOES_NOT_EXISTS, message=i18n.t('basic.data_not_exists', **locale_params))
        while result.code != RESULT_CODE.OK:
            filter_conds, err_msg = format_model_query_conditions(self.model, filters=filters)
            if err_msg:
                result.code = RESULT_CODE.INVALID_PARAM
                result.message = err_msg
                break
            
            try:
                rows, total = await DbProxy().query_list(self.model, filters=filter_conds, limit=limit, offset=offset, sort=orderby, direction=direction, selections=fields)
            except Exception as e:
                LOG.error('get %s tree list failed with error:%s', get_model_class_name(self.model), str(e))
                result.code = RESULT_CODE.INTERNAL_ERROR
                result.message = str(e)
                break

            if not fields:
                if hasattr(self.model, 'as_dict'):
                    formatted_rows = []
                    for row in rows:
                        m = self.model()
                        for k, v in row.items():
                            setattr(m, k, v)
                        formatted_rows.append(getattr(m, 'as_dict')())
                    rows = formatted_rows

            _, pk = model_columns(self.model)
            result.code = RESULT_CODE.OK
            result.message = i18n.t('basic.success', **locale_params)
            result.total = total
            result.data = format_items_as_tree(rows, pk, self.auto_association_keys[id], locale_params)
            if limit:
                result.pageSize = limit
                result.page = int(offset/limit) + 1
        return result

    async def do_edit(self, id: str|int, ignore_empty: bool):
        """
        API handler of edit model instance data
        """
        locale_params = get_locale_params(self.request)
        if not self.form:
            self.set_status(HTTPStatus.INTERNAL_SERVER_ERROR, '%s form not configured for general form handler, please specify form when register model general api handlers' % (get_model_class_name(self.model)))
            self.finish()
            return
        inputs = request_body_as_json(self.request)
        columns, pk = model_columns(self.model)
        inputs[pk] = id
        form_item = self.form(formdata=None, data=inputs, meta={ 'csrf': False })
        result = validate_form(form_item)
        while result.is_success():
            form_pk_id = id
            m = await DbProxy().find_item(self.model, {getattr(self.model, pk)==form_pk_id})
            if not m:
                LOG.warning('get %s [%s] info failed while data does not extsts', get_model_class_name(self.model), str(form_pk_id))
                result = GeneralResponseObject(code=RESULT_CODE.DATA_DOES_NOT_EXISTS, message=i18n.t('basic.data_not_exists', **locale_params)).encode_json()
                break
            if hasattr(m, 'set_session_uid'):
                session_uid = self.session[SESSION_UID_KEY]
                setattr(m, 'set_session_uid', session_uid)
            
            b, msg = await self._check_before_save(form_item)
            if not b:
                result.code = RESULT_CODE.INVALID_PARAM
                result.message = msg
                break
            save_form_fields(form_item, m, ignore_empty=ignore_empty)

            result = GeneralResponseObject(code=RESULT_CODE.FAIL, message=i18n.t('basic.edit_data_failed', **locale_params))
            try:
                res = await DbProxy().update_item(m)
                if res:
                    result.code = RESULT_CODE.OK
                    result.message = i18n.t('basic.success', **locale_params)
                    if hasattr(m, 'as_dict'):
                        result.data = getattr(m, 'as_dict')()
                    else:
                        result.data = dump_model_data(m, columns=columns)
                    LOG.info('edit %s [%s] succeed', get_model_class_name(self.model), str(form_pk_id))
                    if hasattr(form_item, 'after_save'):
                        await self._call(getattr(form_item, 'after_save'), session=self.session, data=m)
                else:
                    LOG.warning('edit %s [%s] failed', get_model_class_name(self.model), str(form_pk_id))
            except Exception as e:
                LOG.error('edit %s [%s] failed with error:%s', get_model_class_name(self.model), str(form_pk_id), str(e))
                result.code = RESULT_CODE.FAIL
                result.message = str(e)
            break
        self.set_header('Content-Type', 'application/json')
        self.write(result.encode_json())
        self.finish()
        
    async def _check_before_save(self, form_item: Form, **kwargs):
        if hasattr(form_item, 'before_save'):
            before_save = getattr(form_item, 'before_save')
            b, msg = await self._call(before_save, session=self.session)
            return b, msg
        return True, ''

    async def _call(self, callable: callable, **kwargs):
        if tornado.gen.is_coroutine_function(callable) or asyncio.iscoroutinefunction(callable):
            return await callable(**kwargs)
        else:
            return callable(**kwargs)

