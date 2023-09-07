import decimal
import json
import sys
import time
from datetime import timedelta
from pathlib import Path
from decimal import Decimal
import math
import random

from django.db.models import Q
from django.forms import model_to_dict
from django.utils import timezone
from django.utils.datetime_safe import datetime
import pytz
from numpy.core.defchararray import upper
from rest_framework import serializers
from main.settings import BASE_DIR
from xj_thread.services.thread_item_service import ThreadItemService
from xj_user.models import BaseInfo
from xj_user.services.user_detail_info_service import DetailInfoService
from xj_user.services.user_platform_service import UserPlatformService
from .finance_service import FinanceService
from ..models import Transact, Currency, PayMode, SandBox, StatusCode
from ..utils.jt import Jt
from ..utils.j_config import JConfig
from ..utils.j_dict import JDict

module_root = str(Path(__file__).resolve().parent)
# 配置之对象
main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))
module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_payment"))

finance_main_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_finance"))
finance_module_config_dict = JDict(JConfig.get_section(path=str(BASE_DIR) + "/config.ini", section="xj_finance"))

# 商户名称
merchant_name = main_config_dict.merchant_name or module_config_dict.merchant_name or ""
sub_appid = main_config_dict.wechat_merchant_app_id or module_config_dict.wechat_merchant_app_id or ""

sand_box_meet = finance_main_config_dict.sand_box_meet or finance_module_config_dict.sand_box_meet or ""
sand_box_receivable = finance_main_config_dict.sand_box_receivable or finance_module_config_dict.sand_box_receivable or ""
sand_box_cash_withdrawal = finance_main_config_dict.sand_box_receivable or finance_module_config_dict.sand_box_cash_withdrawal or ""


class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, int):
                return int(obj)
            elif isinstance(obj, float) or isinstance(obj, decimal.Decimal):
                return float(obj)
            if isinstance(obj, datetime):
                return obj.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(obj, datetime.date):
                return obj.strftime('%Y-%m-%d')
            if isinstance(obj, time) or isinstance(obj, timedelta):
                return obj.__str__()
            else:
                return json.JSONEncoder.default(self, obj)
        except Exception as e:
            # logger.exception(e, stack_info=True)
            return obj.__str__()


# 声明用户序列化
class UserSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        return BaseInfo.objects.create(**validated_data)

    class Meta:
        model = BaseInfo
        # 序列化验证检查，是否要必填的字典
        fields = ['id', 'platform_uid', 'full_name', 'platform_id']


# 声明资金序列化
class FinanceTransactSerializer(serializers.ModelSerializer):
    # 自定义回调函数字段
    lend = serializers.SerializerMethodField()
    amount = serializers.SerializerMethodField()
    income = serializers.SerializerMethodField()
    outgo = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    sand_box = serializers.SerializerMethodField()
    transact_time = serializers.SerializerMethodField()
    transact_timestamp = serializers.SerializerMethodField()
    # sand_box_type_status = serializers.SerializerMethodField()

    # 自定义外键字段
    # platform = serializers.ReadOnlyField(source='platform.platform_name')
    account_name = serializers.ReadOnlyField(source='account.full_name')
    their_account_name = serializers.ReadOnlyField(source='their_account.full_name')
    pay_mode = serializers.ReadOnlyField(source='pay_mode.pay_mode')
    currency = serializers.ReadOnlyField(source='currency.currency')

    def create(self, validated_data):
        """
        Create and return a new `Snippet` instance, given the validated data.
        """
        return Transact.objects.create(**validated_data)

    # 在数据库是否插入内容的字段
    class Meta:
        model = Transact
        fields = [
            'id',
            'transact_no',
            'thread_id',
            'transact_time',
            'transact_timestamp',
            'account_id',
            'account_name',
            'their_account_id',
            'their_account_name',
            'platform_id',
            'enroll_id',
            'order_no',
            'opposite_account',
            'summary',
            'currency',
            'amount',
            'lend',
            'income',
            'outgo',
            'balance',
            'pay_mode',
            'remark',
            'images',
            'sand_box',
            'goods_info',
            'pay_info',
            'finance_status_code',
            'sand_box_status_code',
            'snapshot',
            'goods_info',
        ]

    def get_lend(self, obj):
        income = obj.income if obj.income is not None else Decimal(0)
        outgo = obj.outgo if obj.outgo is not None else Decimal(0)
        amount = income - outgo
        return '借' if amount < 0 else '贷' if amount > 0 else '平'

    # 这里是调用了platform这个字段拼成了get_platform
    def get_amount(self, obj):
        income = obj.income if obj.income is not None else Decimal(0)
        outgo = obj.outgo if obj.outgo is not None else Decimal(0)
        return income - outgo

    def get_income(self, obj):
        return obj.income

    def get_outgo(self, obj):
        return obj.outgo

    def get_balance(self, obj):
        return obj.balance

    def get_sand_box(self, obj):
        return obj.sand_box.sand_box_name if obj.sand_box else None

    def get_transact_time(self, obj):
        return obj.transact_time.astimezone(tz=pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')

    def get_transact_timestamp(self, obj):
        return int(obj.transact_time.timestamp())


class FinanceTransactService:
    @staticmethod
    def get(params, user_id):
        # self.params = request.query_params  # 返回QueryDict类型

        # token = self.request.META.get('HTTP_AUTHORIZATION', '')
        # if not token:
        #     return Response({'err': 4001, 'msg': '缺少Token', })

        # user_id = UserService.check_token(token)
        # if not user_id:
        #     return Response({'err': 4002, 'msg': 'token验证失败', })

        id = params.get('transact_no', None) or params.get('id', None)
        if not id:
            # return Response({'err': 6001, 'msg': '缺少id', })
            return None, '缺少id'

        transact = Transact.objects.filter(id=id).first()
        # print(">>> transact:", transact)
        if not transact:
            return None, '记录不存在'

        serializer = FinanceTransactSerializer(transact, many=False)
        # print(">>> serializer:", serializer)

        # # 翻译
        # output = _("Welcome to my site.")

        return serializer.data, None

        # POST方法，如果无transact_no则是新增，否则为修改

    @staticmethod
    def finance_transact_detailed(transact_no):
        transact = Transact.objects.filter(transact_no=transact_no).first()
        if not transact:
            return None, "不存在"
        return transact, None

    @staticmethod
    def finance_flow_writing(params, finance_type=None):

        amount = params.get('amount', 0.0)  # 如果是负数是应付反之是应收
        enroll_id = params.get('enroll_id', None)  # 报名id
        order_no = params.get('order_no', None)  # 订单号
        summary = params.get('summary', None)  # 摘要
        transact_no = params.get('transact_no', None)  # 订单号
        account_id = params.get("account_id", None)
        pay_mode = params.get("pay_mode", None)
        goods_info = params.get("goods_info", None)
        sand_box_status_code = params.get("sand_box_status_code", None)
        sand_box = params.get("sand_box", None)
        currency = params.get("currency", "CNY")
        images = params.get("images", "")
        action = params.get("action", "支付")
        user_finance_data = {
            'account_id': account_id,
            'their_account_name': sub_appid,
            'currency': currency,
            'pay_mode': pay_mode,
            'platform': merchant_name,
        }

        platform_finance_data = {
            'account_name': sub_appid,
            'their_account_id': account_id,
            'currency': currency,
            'pay_mode': pay_mode,
            'platform': merchant_name,

        }
        # 判断金额
        if not amount:
            return None, "金额不能为空"
        # 判断是否接收报名id
        if enroll_id:
            user_finance_data['enroll_id'] = enroll_id
            platform_finance_data['enroll_id'] = enroll_id
        # 判断是否接收订单号
        if order_no:
            user_finance_data['order_no'] = order_no
            platform_finance_data['order_no'] = order_no
        else:
            user_finance_data['order_no'] = FinanceService.make_unicode()
            platform_finance_data['order_no'] = FinanceService.make_unicode()

        if not transact_no:
            transact_no = FinanceService.make_unicode(user_finance_data['order_no'])

        if sand_box:
            user_finance_data['sand_box'] = sand_box  # 沙盒应付
            platform_finance_data['sand_box'] = sand_box  # 沙盒应付
        # 生成摘要
        user_set, err = DetailInfoService.get_detail(account_id)
        user_platform_set, platform_err = DetailInfoService.get_detail(search_params={"nickname": sub_appid})
        project_name = None
        # 用户报名通知代码块
        if user_set:
            print(user_platform_set)
            if enroll_id:
                # 如果存在报名id 查询报名记录
                if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
                    from xj_enroll.service.enroll_services import EnrollServices
                enroll_set, enroll_err = EnrollServices.enroll_detail(enroll_id)
                if enroll_set:
                    # 根据报名记录获取 信息模块项目基本信息
                    thread_set, thread_err = ThreadItemService.detail(enroll_set['thread_id'])
                    if thread_set:
                        project_name = thread_set['title']
        summary_content = "【" + user_set['full_name'] + "】" + action + "【" + user_platform_set[
            'full_name'] + "】项目名称【" + project_name + "】款项"

        user_finance_data['summary'] = summary_content
        platform_finance_data['summary'] = summary_content

        if goods_info:
            user_finance_data['goods_info'] = goods_info
            platform_finance_data['goods_info'] = goods_info
        if sand_box_status_code:
            user_finance_data['sand_box_status_code'] = str(upper(sand_box_status_code))
            platform_finance_data['sand_box_status_code'] = str(upper(sand_box_status_code))

        if images:
            user_finance_data['images'] = images
            platform_finance_data['images'] = images

        # 充值行为（线上支付 生成真实记录）|转账行为（线下支付 生成沙盒记录 审核成功后核销沙盒 生成真实记录）
        if finance_type == "RECHARGE" or finance_type == "TRANSFER":
            try:
                if finance_type == "TRANSFER":
                    user_finance_data['sand_box'] = sand_box_meet  # 沙盒应付
                    platform_finance_data['sand_box'] = sand_box_receivable  # 沙盒应收

                user_finance_data['amount'] = -abs(float(amount))
                user_finance_data['transact_no'] = str(transact_no) + "-1"
                user_finance_data['finance_status_name'] = "待接单"  # 资金状态码 finance_status_code 43 已下单支付 待接单
                # user_finance_data['money_flow'] = "TRANSFER"  # 资金流行为
                user_add_data, user_err_txt = FinanceTransactService.post(user_finance_data)
                if user_err_txt:
                    # print(">>>>payment_logic_processing_err", user_err_txt)
                    # logger.info(">>>>payment_logic_processing" + "写入资金模块失败")
                    return None, user_err_txt
                platform_finance_data['amount'] = float(amount)
                platform_finance_data['transact_no'] = str(transact_no) + "-2"
                platform_finance_data['finance_status_name'] = "待接单"  # 资金状态码 finance_status_code 43 已下单支付 待接单
                # platform_finance_data['money_flow'] = "TRANSFER"  # 沙盒应收
                finance_add_data, err_txt = FinanceTransactService.post(platform_finance_data)
                if err_txt:
                    return None, err_txt
                return user_finance_data['order_no'], None
            except Exception as e:
                return None, str(e)
        # 支付行为 （由平台对用户进行余额转账）
        elif finance_type == "PAY":  # 支付行为
            try:
                user_finance_data['sand_box'] = sand_box_receivable  # 沙盒应收
                user_finance_data['amount'] = float(amount)
                user_finance_data['order_no'] = FinanceService.make_unicode()
                user_finance_data['transact_no'] = FinanceService.make_unicode(str(user_finance_data['account_id']))
                user_finance_data['finance_status_name'] = "待付款"  # 资金状态码 finance_status_code 242 报名成功 待付款
                user_add_data, user_err_txt = FinanceTransactService.post(user_finance_data)
                if user_err_txt:
                    return None, user_err_txt
                platform_finance_data['sand_box'] = sand_box_meet  # 沙盒应付
                platform_finance_data['amount'] = -abs(float(amount))
                platform_finance_data['order_no'] = FinanceService.make_unicode()
                platform_finance_data['transact_no'] = FinanceService.make_unicode(
                    str(platform_finance_data['account_name']))
                platform_finance_data['finance_status_name'] = "待付款"  # 资金状态码 finance_status_code 242 报名成功 待付款
                finance_add_data, err_txt = FinanceTransactService.post(platform_finance_data)
                if err_txt:
                    return None, err_txt
                return user_finance_data['order_no'], None

            except Exception as e:
                return None, str(e)
        # 提现行为
        elif finance_type == "WITHDRAW":
            user_finance_data['sand_box'] = sand_box_cash_withdrawal  # 提现
            user_finance_data['amount'] = -abs(float(amount))
            user_finance_data['order_no'] = FinanceService.make_unicode()
            finance_add_data, err_txt = FinanceTransactService.post(user_finance_data)
            if err_txt:
                return None, None
            return user_finance_data['order_no'], None
        else:
            return order_no, "资金类型不存在"

    @staticmethod
    def post(param):
        item = serializer_params = {}  # 将要写入的某条数据

        # ========== 一、验证权限 ==========

        # token = self.request.META.get('HTTP_AUTHORIZATION', '')
        # if not token:
        #     return Response({'err': 4001, 'msg': '缺少Token', })
        # user_id = UserService.check_token(token)
        # if not user_id:
        #     return Response({'err': 4002, 'msg': 'token验证失败', })

        # ========== 二、必填性检查 ==========
        # if not param.get('platform', '') and not param.get('platform_id', ''):
        #     return None, '缺少platform'
        if not param.get('amount', '') and not param.get('income', '') and not param.get('outgo', ''):
            return None, '缺少amount'
        if not param.get('currency', '') and not param.get('currency_id', ''):
            return None, '缺少currency'
        if not param.get('pay_mode', '') and not param.get('pay_mode_id', ''):
            return None, '缺少pay_mode'
        # if not param.get('summary', ''):
        #     return None, '缺少summary'
        # ========== 三、内容的类型准确性检查 ==========
        # 判断无transact_no为新建，否则为修改
        is_create = True
        item['sand_box'] = None
        item['snapshot'] = None
        transact_has_id = Transact.objects.filter(transact_no=param.get('transact_no', '')).first()
        if transact_has_id:
            res_data = model_to_dict(transact_has_id)
            if not res_data['sand_box']:
                return None, '非沙盒数据不允许修改'
            is_create = False

        # 检查是否有该id
        if not is_create and param.get('id', ''):
            has_id = Transact.objects.filter(id=param.get('id', '')).count() > 0
            if not has_id:
                return None, 'id不存在'
        # 判断平台是否存在
        if not param.get('platform_id', ''):
            platform_name = param.get('platform', '')
            if not platform_name:
                platform_name = merchant_name

            platform_info, err = UserPlatformService.get_platform_info(platform_name=platform_name)
            if err:
                return None, '平台不存在: ' + platform_name
            item['platform_id'] = platform_info.get('platform_id')
        else:
            item['platform_id'] = param.get('platform_id', '')
        # 发起交易的账号ID，如果没有则默认自己
        account_id = int(param.get('account_id', 0))
        account_name = (param.get('account_name', ''))
        if account_id:
            item['account'] = BaseInfo.objects.filter(id=account_id).first()
            if not item['account']:
                return None, '用户account_id不存在'
        elif not account_id and account_name:
            item['account'] = BaseInfo.objects.filter(nickname=account_name).first()
            if not item['account']:
                return None, '用户account_id不存在'
        # 承受交易的账号，要从数据库判断是否存在
        their_account_id = param.get('their_account_id', '')
        if their_account_id:
            their_account_id = int(their_account_id)
            item['their_account'] = BaseInfo.objects.filter(id=their_account_id).first()
            if not item['their_account']:
                return None, '用户their_account_id不存在'
        # 边界检查，自己不能和自己交易
        # if account_id == their_account_id:
        #     return None, '自己不能和自己交易'
        # 生成发起交易的用户名 todo 要不用金额会不会更安全？怎么处理重复的可能性
        username = item['account'].user_name
        # 生成唯一且不可重复的交易ID，且具有校验作用
        if is_create and param.get('transact_no', ''):

            transact_no = param.get('transact_no', '')
        elif is_create and not param.get('transact_no', ''):
            transact_no = FinanceService.make_unicode(username)
        else:
            transact_no = param.get('transact_no', '')

        item['transact_no'] = transact_no
        if is_create and Transact.objects.filter(transact_no=transact_no).values().count():
            return None, '新增时发现复重交易ID，请检查是否有重复记录: ' + transact_no
        if not is_create and Transact.objects.filter(transact_no=transact_no).values().count() == 0:
            return None, '修改信息的交易ID不存在: ' + transact_no
        tz = pytz.timezone('Asia/Shanghai')
        # 返回datetime格式的时间
        now_time = timezone.now().astimezone(tz=tz).strftime("%Y-%m-%d %H:%M:%S")
        now = datetime.strptime(now_time, '%Y-%m-%d %H:%M:%S')
        # 如果没有时间则生成交易时间
        transact_time = str(param.get('transact_time', ''))
        # if transact_time else timezone.localtime() if is_create TODO USE_TZ = False 时会报错 如果USE_TZ设置为True时，Django会使用系统默认设置的时区，即America/Chicago，此时的TIME_ZONE不管有没有设置都不起作用。
        item['transact_time'] = datetime.strptime(transact_time, '%Y-%m-%d %H:%M:%S') \
            if transact_time else now if is_create \
            else Transact.objects.filter(transact_no=transact_no).first().transact_time
        if not item['transact_time']:
            return None, '交易时间格式不正确'

        # 边界检查：币种是否存在
        if not param.get('currency_id', ''):
            currency = param.get('currency', '')
            item['currency_set'] = Currency.objects.filter(currency=currency).first()
            if item['currency_set'] is None:
                return None, 'currency不存在'
            item['currency'] = item['currency_set'].id
        else:
            item['currency_set'] = Currency.objects.filter(id=param.get('currency_id', '')).first()
            if item['currency_set'] is None:
                return None, 'currency不存在'
            item['currency'] = param.get('currency_id', '')

        # 判断支付方式，并根据支付方式判断是否要从内部余额中扣款
        if not param.get('pay_mode_id', ''):
            pay_mode = param.get('pay_mode', '')
            # 边界检查：支付方式是否存在
            item['pay_mode_set'] = PayMode.objects.filter(pay_mode=pay_mode).first()
            if item['pay_mode_set'] is None:
                return None, 'pay_mode不存在'
            item['pay_mode'] = item['pay_mode_set'].id
        else:
            item['pay_mode_set'] = PayMode.objects.filter(id=param.get('pay_mode_id', '')).first()
            if item['pay_mode_set'] is None:
                return None, 'pay_mode不存在'
            item['pay_mode'] = param.get('pay_mode_id', '')

            # 支出或收入 ----------------------------------------------------------------------
        if not param.get('income', '') and not param.get('outgo', ''):
            if not Jt.is_number(param.get('amount', '')):
                return None, 'amount必须是数字'
            amount = Decimal(param.get('amount', 0.0))  # todo 财务系统不存在四舍五入，一分都不多给
            if amount == 0:
                return None, '交易金额不能为0'
            income = amount if amount > 0 else Decimal(0.0)
            item['income'] = income
            outgo = Decimal(math.fabs(amount)) if amount < 0 else Decimal(0.0)
            item['outgo'] = outgo
        else:
            income = float(param.get('income', 0.0))
            item['income'] = income
            outgo = float(param.get('outgo', 0.0))
            item['outgo'] = outgo

        enroll_id = param.get('enroll_id', '')
        if enroll_id:
            item['enroll_id'] = enroll_id

        if param.get('finance_status_code', ''):
            # item['status_code_set'] = StatusCode.objects.filter(
            #     id=param.get('finance_status_code', '')).first()
            # if item['status_code_set'] is None:
            #     return None, 'status_code不存在'
            # item['finance_status_code'] = item['status_code_set'].id
            item['status_code_set'] = StatusCode.objects.filter(
                finance_status_code=param.get('finance_status_code', '')).first()
            if item['status_code_set'] is None:
                return None, 'status_code不存在'
            item['finance_status_code'] = item['status_code_set'].finance_status_code
        elif not param.get('finance_status_code', '') and param.get('finance_status_name', ''):
            item['status_code_set'] = StatusCode.objects.filter(
                finance_status_name=param.get('finance_status_name', '')).first()
            if item['status_code_set'] is None:
                return None, 'status_code不存在'
            # item['finance_status_code'] = item['status_code_set'].id
            item['finance_status_code'] = item['status_code_set'].finance_status_code

        if param.get('sand_box_status_code', ""):
            item['sand_box_status_code'] = param.get('sand_box_status_code', "")

        # 沙盒 ----------------------------------------------------------------------
        sand_box_name = param.get('sand_box', '')
        if is_create:
            if sand_box_name:
                item['sand_box_set'] = SandBox.objects.filter(sand_box_name=sand_box_name).first()
                if item['sand_box_set'] is None:
                    return None, 'sand_box不存在'
                item['sand_box'] = item['sand_box_set'].id
        else:
            item['sand_box_set'] = SandBox.objects.filter(id=res_data['sand_box']).first()
            if item['sand_box_set'] is None:
                return None, 'sand_box不存在'
            item['sand_box'] = item['sand_box_set'].id

        # SandBox.objects.filter(sand_box_name=sand_box_name).first()
        # 查余额 ---------------------------------------------------------------------
        balance_set = Transact.objects.filter(
            Q(account_id=account_id) &
            Q(currency_id=item['currency']) &
            Q(platform_id=item['platform_id'])&
            Q(transact_time__lt=item['transact_time']) &
            ~Q(transact_no=item['transact_no'])
        )
        # 信息模块id
        thread_id = param.get('thread_id', '')
        if thread_id:
            item['thread_id'] = thread_id
        # 快照
        goods_info = param.get('goods_info', '')
        # print(goods_info)
        if goods_info:
            jsDumps = json.dumps(goods_info, cls=DateEncoder)
            jsLoads = json.loads(jsDumps)
            enroll_list = []
            if 'enroll' in jsLoads:
                if not sys.modules.get("xj_enroll.service.enroll_services.EnrollServices"):
                    from xj_enroll.service.enroll_services import EnrollServices
                if isinstance(goods_info['enroll'], dict):
                    EnrollServices.enroll_edit(params={"finance_invoicing_code": "INVOICING"},
                                               search_param={"enroll_id": goods_info['enroll']['id']})
                else:
                    for i in goods_info['enroll']:
                        enroll_list.append(int(i['id']))
                    EnrollServices.enroll_edit(params={"finance_invoicing_code": "INVOICING"},
                                               search_param={"enroll_id_list": enroll_list})
            # else:
            #     print('不存在')
            item['goods_info'] = jsLoads

        # 如果有沙盒。
        if item['sand_box']:
            balance_set = balance_set.filter(Q(sand_box_id=item['sand_box']))
        else:
            balance_set = balance_set.filter(Q(sand_box_id__isnull=True))

        balance_set = balance_set.order_by('-transact_time').values().first()
        last_balance = balance_set['balance'] if balance_set is not None else Decimal(0.0)

        # item['balance'] = last_balance
        # if item['pay_mode_set'].pay_mode == "BALANCE":
        balance = float(last_balance) + float(income) - float(outgo)
        item['balance'] = balance

        # print(item['balance'])
        # 平台订单号是可以允许重复的，如果没有平台订单号则输入交易号
        order_no = (param.get('order_no', transact_no))  # 如果没有平台订单号则填交易号
        item['order_no'] = order_no

        # 对方科目
        opposite_account = param.get('opposite_account', '')
        item['opposite_account'] = opposite_account

        # 摘要
        item['summary'] = "摘要...."
        summary = param.get('summary', '')
        if summary:
            item['summary'] = summary
        elif not summary and param.get("sand_box_status_code", ""):
            if param.get("sand_box_status_code", "") == "INVOICING":
                item['summary'] = "开票"
            elif param.get("sand_box_status_code", "") == "WITHDRAWING":
                item['summary'] = "提现"
            elif param.get("sand_box_status_code", "") == "TRANSFERING":
                item['summary'] = "转账"

        # # 商品信息
        # goods_info = param.get('goods_info', '')
        # item['goods_info'] = goods_info

        # 支付信息
        pay_info = param.get('pay_info', '')
        item['pay_info'] = pay_info

        # 备注
        remark = param.get('remark', '')
        item['remark'] = remark

        # 上传图片
        images = param.get('images', '')
        item['images'] = images

        # ========== 四、相关前置业务逻辑处理 ==========

        # 在新建订单时：如果平台订单号重复，金额不能重复，收方和支出方不能重复，金额也不能重复。
        if is_create:
            repeat_order_set = Transact.objects.filter(
                Q(sand_box_id=item['sand_box']) &
                Q(order_no=order_no) &
                Q(account_id=account_id) &
                (Q(income=income) | Q(outgo=outgo))
            )
            # 单独判断，当有对方账号ID时才判断，因为在设计上对方账号是可以自动生成的
            if their_account_id:
                repeat_order_set.filter(Q(their_account_id=their_account_id))
            # if repeat_order_set.count() > 0:
            # return Response({'err': 1015, 'msg': '重复的交易订单号：' + str(order_no), })
            # return None, '重复的交易订单号：' + str(order_no)
        # --------------------------------------------------------------------------------------

        if param.get('their_account_name', ''):
            their_account_name = param.get('their_account_name', '')
        else:
            their_account_name = sub_appid

            # return Response({'err': 1016, 'msg': 'their_account_id或their_account_name 必填', })
            # return None, 'their_account_id或their_account_name 必填'
        # 没有对方账户ID时从对方账户名创建一个账户
        # 如果无their_account_id、有their_account_name，则用their_account_name生成一个their_account_id
        if not param.get('their_account_id', '') and their_account_name:
            # their_account_name = param['their_account_name']
            base_info = BaseInfo.objects.filter(nickname=their_account_name).first()
            # print(their_account_name)
            if base_info:
                base_info = model_to_dict(base_info)
                item['their_account_id'] = base_info['id']
                item['their_account'] = BaseInfo.objects.get(id=item['their_account_id'])
            else:
                new_user_param = {
                    "full_name": their_account_name,
                    "nickname": their_account_name,
                }
                new_user = BaseInfo.objects.create(**new_user_param)
                item['their_account_id'] = new_user.id
                item['their_account'] = BaseInfo.objects.get(id=item['their_account_id'])
        # -------------------------------------------------------------------------------------

        # 如果有id，则是修改数据
        if is_create:
            # print()
            response = FinanceTransactService.create(item)
        else:
            # print()
            response = FinanceTransactService.update(item)
        # return None
        return response

    # 增
    @staticmethod
    def create(item):
        # 增加一个交易记录
        serializer = FinanceTransactSerializer(data=item, context={})

        # 验证失败，获取错误信息
        if not serializer.is_valid():
            # print(">>> serializer.errors:", serializer.errors, "\n")
            # 调用save(), 从而调用序列化对象的create()方法,创建一条数据
            # return Response({'err': 1018, 'msg': serializer.errors, })
            return None, serializer.errors

        # 验证成功，获取数据
        serializer.validated_data['platform_id'] = item['platform_id']
        serializer.validated_data['account'] = item['account']
        serializer.validated_data['enroll_id'] = item.get('enroll_id', None)
        serializer.validated_data['their_account'] = item['their_account']
        serializer.validated_data['pay_mode'] = item['pay_mode_set']
        serializer.validated_data['currency'] = item['currency_set']
        serializer.validated_data['sand_box'] = item.get('sand_box_set', None)
        serializer.validated_data['income'] = item['income']
        serializer.validated_data['outgo'] = item['outgo']
        serializer.validated_data['balance'] = item['balance']
        serializer.validated_data['transact_time'] = item['transact_time']
        serializer.validated_data['finance_status_code'] = item.get('finance_status_code', None)
        serializer.validated_data['thread_id'] = item.get('thread_id', None)
        serializer.validated_data['sand_box_status_code'] = item.get('sand_box_status_code', None)
        serializer.validated_data['goods_info'] = item.get('goods_info', None)
        serializer.validated_data['images'] = item.get('images', None)

        # print(">>> serializer.validated_data: ", serializer.validated_data,)
        # print(">>> serializer: ", serializer,)

        serializer.save()

        FinanceService.check_balance(account_id=item['account'].id,
                                     platform_id=item['platform_id'],
                                     currency=item['currency_set'].currency,
                                     sand_box=item.get('sand_box_set', None))

        # return Response({
        #     'err': 0,
        #     'msg': '新增成功',
        # })
        return None, None

    # 改
    @staticmethod
    def update(item):
        # print(">>> update:", item, )

        transact = Transact.objects.filter(transact_no=item['transact_no']).first()
        update_serializer = FinanceTransactSerializer(data=item, instance=transact)
        if not update_serializer.is_valid():
            # print(">>> serializer.errors:", serializer.errors, "\n")
            # 调用save(), 从而调用序列化对象的create()方法,创建一条数据
            # return Response({'err': 1019, 'msg': update_serializer.errors, })
            return None, update_serializer.errors
        # 验证成功，获取数据
        update_serializer.validated_data['platform_id'] = item.get('platform_id', None)
        update_serializer.validated_data['account'] = item['account']
        update_serializer.validated_data['enroll_id'] = item.get('enroll_id', None)
        update_serializer.validated_data['their_account'] = item.get('their_account', None)
        update_serializer.validated_data['pay_mode'] = item['pay_mode_set']
        update_serializer.validated_data['currency'] = item['currency_set']
        update_serializer.validated_data['sand_box'] = item.get('sand_box_set', None)
        update_serializer.validated_data['income'] = item.get('income', None)
        update_serializer.validated_data['outgo'] = item.get('outgo', None)
        update_serializer.validated_data['balance'] = item['balance']
        update_serializer.validated_data['transact_time'] = item['transact_time']
        update_serializer.validated_data['images'] = item.get('images', None)
        # update_serializer.validated_data['sand_box_type_status'] = item.get('sand_box_type_status', None)
        update_serializer.save()

        FinanceService.check_balance(account_id=item['account'].id,
                                     platform_id=item['platform_id'],
                                     currency=item['currency_set'].currency,
                                     sand_box=item.get('sand_box_set', None))

        # return Response({
        #     'err': 0,
        #     'msg': '更新成功',
        # })
        return None, None

    # 生成随机的4位数数字
    @staticmethod
    def random_four_int():
        str = ""
        for i in range(4):
            ch = chr(random.randrange(ord('0'), ord('9') + 1))
            str += ch
        return str

    @staticmethod
    def get_finance_by_user(user_id):
        user_finance = Transact.objects.filter(account_id=user_id).order_by("-id").values()
        if not user_finance:
            return None, None
        return user_finance.first(), None
