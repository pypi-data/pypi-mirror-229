# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.abstract_client import AbstractClient
from tencentcloud.ess.v20201111 import models


class EssClient(AbstractClient):
    _apiVersion = '2020-11-11'
    _endpoint = 'ess.tencentcloudapi.com'
    _service = 'ess'


    def BindEmployeeUserIdWithClientOpenId(self, request):
        """将电子签系统员工userId与客户系统员工openId进行绑定

        :param request: Request instance for BindEmployeeUserIdWithClientOpenId.
        :type request: :class:`tencentcloud.ess.v20201111.models.BindEmployeeUserIdWithClientOpenIdRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.BindEmployeeUserIdWithClientOpenIdResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("BindEmployeeUserIdWithClientOpenId", params, headers=headers)
            response = json.loads(body)
            model = models.BindEmployeeUserIdWithClientOpenIdResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CancelFlow(self, request):
        """用于撤销签署流程
        适用场景：如果某个合同流程当前至少还有一方没有签署，则可通过该接口取消该合同流程。常用于合同发错、内容填错，需要及时撤销的场景。
        注：如果合同流程中的参与方均已签署完毕，则无法通过该接口撤销合同。

        :param request: Request instance for CancelFlow.
        :type request: :class:`tencentcloud.ess.v20201111.models.CancelFlowRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CancelFlowResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CancelFlow", params, headers=headers)
            response = json.loads(body)
            model = models.CancelFlowResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CancelMultiFlowSignQRCode(self, request):
        """此接口（CancelMultiFlowSignQRCode）用于取消一码多扫二维码。该接口对传入的二维码ID，若还在有效期内，可以提前失效。

        :param request: Request instance for CancelMultiFlowSignQRCode.
        :type request: :class:`tencentcloud.ess.v20201111.models.CancelMultiFlowSignQRCodeRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CancelMultiFlowSignQRCodeResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CancelMultiFlowSignQRCode", params, headers=headers)
            response = json.loads(body)
            model = models.CancelMultiFlowSignQRCodeResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CancelUserAutoSignEnableUrl(self, request):
        """此接口（CancelUserAutoSignEnableUrl）用来撤销发送给个人用户的自动签开通链接，撤销后对应的个人用户开通链接失效。若个人用户已经完成开通，将无法撤销。（处方单场景专用，使用此接口请与客户经理确认）

        :param request: Request instance for CancelUserAutoSignEnableUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CancelUserAutoSignEnableUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CancelUserAutoSignEnableUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CancelUserAutoSignEnableUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CancelUserAutoSignEnableUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateBatchCancelFlowUrl(self, request):
        """注：此接口将会废弃，请使用撤销单个签署流程（CancelFlow）接口。
        指定需要批量撤回的签署流程Id，获取批量撤销链接。
        客户指定需要撤回的签署流程Id，最多100个，超过100不处理；接口调用成功返回批量撤回合同的链接，通过链接跳转到电子签小程序完成批量撤回。

        :param request: Request instance for CreateBatchCancelFlowUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateBatchCancelFlowUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateBatchCancelFlowUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateBatchCancelFlowUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CreateBatchCancelFlowUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateChannelSubOrganizationModifyQrCode(self, request):
        """根据产品要求，调整接口目录

        新接口：ChannelCreateOrganizationModifyQrCode

        老接口目前无线上流量，测试用例已下线处理

        生成子客编辑企业信息二维码

        :param request: Request instance for CreateChannelSubOrganizationModifyQrCode.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateChannelSubOrganizationModifyQrCodeRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateChannelSubOrganizationModifyQrCodeResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateChannelSubOrganizationModifyQrCode", params, headers=headers)
            response = json.loads(body)
            model = models.CreateChannelSubOrganizationModifyQrCodeResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateConvertTaskApi(self, request):
        """上传了word、excel、图片文件后，通过该接口发起文件转换任务，将word、excel、图片文件转换为pdf文件。

        :param request: Request instance for CreateConvertTaskApi.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateConvertTaskApiRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateConvertTaskApiResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateConvertTaskApi", params, headers=headers)
            response = json.loads(body)
            model = models.CreateConvertTaskApiResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateDocument(self, request):
        """创建签署流程电子文档
        适用场景：见创建签署流程接口。
        注：该接口需要给对应的流程指定一个模板id，并且填充该模板中需要补充的信息。是“发起流程”接口的前置接口。

        :param request: Request instance for CreateDocument.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateDocumentRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateDocumentResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateDocument", params, headers=headers)
            response = json.loads(body)
            model = models.CreateDocumentResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateEmbedWebUrl(self, request):
        """本接口（CreateEmbedWebUrl）用于创建嵌入web的链接 本接口支持创建：创建印章，创建模板，修改模板，预览模板，预览合同流程的web链接 进入web连接后与当前控制台操作保持一致

        :param request: Request instance for CreateEmbedWebUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateEmbedWebUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateEmbedWebUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateEmbedWebUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CreateEmbedWebUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlow(self, request):
        """通过模板创建签署流程<br/>
        适用场景：在标准制式的合同场景中，可通过提前预制好模板文件，每次调用模板文件的id，补充合同内容信息及签署信息生成电子合同。<br/>
        注：该接口是通过模板生成合同流程的前置接口，先创建一个不包含签署文件的流程。<br/>
        配合“创建电子文档”接口和“发起流程”接口使用。<br/>

        :param request: Request instance for CreateFlow.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlow", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowApprovers(self, request):
        """### 适用场景
        在通过模板或者文件发起合同时，若未指定企业签署人信息，则流程发起后，可以调用此接口补充或签签署人。
        同一签署人可以补充多个员工作为或签签署人,最终实际签署人取决于谁先领取合同完成签署。
        ### 限制条件
        -  本企业(发起方企业)支持通过企业微信UserId 或者 姓名+手机号补充
        - 他方企业仅支持通过姓名+手机号补充

        :param request: Request instance for CreateFlowApprovers.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowApproversRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowApproversResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowApprovers", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowApproversResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowByFiles(self, request):
        """此接口（CreateFlowByFiles）用来通过上传后的pdf资源编号来创建待签署的合同流程。<br/>
        适用场景1：适用非制式的合同文件签署。一般开发者自己有完整的签署文件，可以通过该接口传入完整的PDF文件及流程信息生成待签署的合同流程。<br/>
        适用场景2：可通过该接口传入制式合同文件，同时在指定位置添加签署控件。可以起到接口创建临时模板的效果。如果是标准的制式文件，建议使用模板功能生成模板ID进行合同流程的生成。<br/>
        注意事项：该接口需要依赖“多文件上传”接口生成pdf资源编号（FileIds）进行使用。<br/>

        :param request: Request instance for CreateFlowByFiles.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowByFilesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowByFilesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowByFiles", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowByFilesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowEvidenceReport(self, request):
        """创建出证报告并返回报告ID。
        使用此功能需搭配出证套餐。
        注意：出证过程需一定时间，建议在调用创建出证后的24小时之后，通过DescribeFlowEvidenceReport接口进行查询。

        :param request: Request instance for CreateFlowEvidenceReport.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowEvidenceReportRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowEvidenceReportResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowEvidenceReport", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowEvidenceReportResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowGroupByFiles(self, request):
        """此接口（CreateFlowGroupByFiles）通过多文件创建合同组签署流程。<br/>
        PDF资源Id 通过上传文件接口获取
        此接口合同组中的子合同必须都是文件发起的合同

        :param request: Request instance for CreateFlowGroupByFiles.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowGroupByFilesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowGroupByFilesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowGroupByFiles", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowGroupByFilesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowGroupByTemplates(self, request):
        """此接口（CreateFlowGroupByTemplates）通过多模板创建合同组签署流程。<br/>
        此接口合同组中的子合同必须都是模板发起的合同。 <br/>目前最大仅支持50个子合同

        :param request: Request instance for CreateFlowGroupByTemplates.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowGroupByTemplatesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowGroupByTemplatesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowGroupByTemplates", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowGroupByTemplatesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowReminds(self, request):
        """指定需要批量催办的签署流程ID，批量催办合同，最多100个。需要符合以下条件的合同才可被催办：

        1. 发起合同时，签署人的NotifyType需设置为sms
        2. 合同中当前状态为“待签署”的签署人是催办的对象
        3. 每个合同只能催办一次

        注意：该接口无法直接调用，请联系客户经理申请使用。

        :param request: Request instance for CreateFlowReminds.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowRemindsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowRemindsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowReminds", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowRemindsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowSignReview(self, request):
        """提交企业签署流程审批结果
        适用场景:
        在通过接口(CreateFlow 或者CreateFlowByFiles)创建签署流程时，若指定了参数 NeedSignReview 为true，且发起方企业作为签署方参与了流程签署，则可以调用此接口提交企业内部签署审批结果。
        若签署流程状态正常，且本企业存在签署方未签署，同一签署流程可以多次提交签署审批结果，签署时的最后一个“审批结果”有效。

        :param request: Request instance for CreateFlowSignReview.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowSignReviewRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowSignReviewResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowSignReview", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowSignReviewResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateFlowSignUrl(self, request):
        """创建个人H5签署链接，请联系客户经理申请开通使用, 否则调用会返回失败 <br/>

        该接口用于发起合同后，生成个人签署人的签署链接, 暂时不支持企业端签署 <br/>

        注意：该接口目前签署人类型仅支持个人签署方（PERSON） <br/>
        注意：该接口可生成签署链接的C端签署人必须仅有手写签名和时间类型的签署控件<br/>
        注意：该接口返回的签署链接是用于APP集成的场景，支持APP打开或浏览器直接打开，不支持微信小程序嵌入。微信小程序请使用小程序跳转或半屏弹窗的方式<br/>

        :param request: Request instance for CreateFlowSignUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateFlowSignUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateFlowSignUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateFlowSignUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CreateFlowSignUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateIntegrationDepartment(self, request):
        """通过此接口，创建企业的部门，支持绑定客户系统部门ID。

        :param request: Request instance for CreateIntegrationDepartment.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationDepartmentRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationDepartmentResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateIntegrationDepartment", params, headers=headers)
            response = json.loads(body)
            model = models.CreateIntegrationDepartmentResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateIntegrationEmployees(self, request):
        """创建员工,此接口会发送提醒员工实名的短信，如果通过手机号发现员工已经创建，则不会重新创建，会发送短信提醒员工实名
        注意：此接口支持企微组织架构的 openid 创建员工，这种场景下传递明文的企微 openid 到WeworkOpenId字段即可（企微明文的 openid 一定要在应用的可见范围内才行），通过企微创建的员工，会发送企微消息去提醒实名

        :param request: Request instance for CreateIntegrationEmployees.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationEmployeesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationEmployeesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateIntegrationEmployees", params, headers=headers)
            response = json.loads(body)
            model = models.CreateIntegrationEmployeesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateIntegrationRole(self, request):
        """此接口（CreateIntegrationRole）用来创建企业自定义的SaaS角色或集团角色。

        适用场景1：创建当前企业的自定义SaaS角色或集团角色，并且创建时不进行权限的设置（PermissionGroups 参数不传），角色中的权限内容可通过控制台编辑角色或通过接口 ModifyIntegrationRole 完成更新。

        适用场景2：创建当前企业的自定义SaaS角色或集团角色，并且创建时进行权限的设置（PermissionGroups 参数要传），权限树内容 PermissionGroups 可参考接口 DescribeIntegrationRoles 的输出。
        适用场景3：创建集团角色时可同时设置角色管理的子企业列表，可通过设置 SubOrganizationIds 参数达到此效果。

        适用场景4：主企业代理子企业操作的场景，需要设置Agent参数，并且ProxyOrganizationId设置为子企业的id即可。

        注意事项：SaaS角色和集团角色对应的权限树是不一样的。

        :param request: Request instance for CreateIntegrationRole.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationRoleRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationRoleResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateIntegrationRole", params, headers=headers)
            response = json.loads(body)
            model = models.CreateIntegrationRoleResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateIntegrationUserRoles(self, request):
        """绑定员工与对应角色

        :param request: Request instance for CreateIntegrationUserRoles.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationUserRolesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateIntegrationUserRolesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateIntegrationUserRoles", params, headers=headers)
            response = json.loads(body)
            model = models.CreateIntegrationUserRolesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateMultiFlowSignQRCode(self, request):
        """此接口（CreateMultiFlowSignQRCode）用于创建一码多扫流程签署二维码。
        适用场景：无需填写签署人信息，可通过模板id生成签署二维码，签署人可通过扫描二维码补充签署信息进行实名签署。常用于提前不知道签署人的身份信息场景，例如：劳务工招工、大批量员工入职等场景。

        **本接口适用于发起方没有填写控件的 B2C或者单C模板**

        **若是B2C模板,还要满足以下任意一个条件**
        - 模板中配置的签署顺序是无序
        - B端企业的签署方式是静默签署
        - B端企业是非首位签署

         通过一码多扫二维码发起的合同，涉及到的合同回调消息可参考文档[合同发起以及签署相关回调](https://qian.tencent.com/developers/company/callback_types_contracts_sign)

        用户通过签署二维码发起合同时，因企业额度不足导致失败 会触发签署二维码相关回调,具体参考文档[签署二维码相关回调](https://qian.tencent.com/developers/company/callback_types_commons#%E7%AD%BE%E7%BD%B2%E4%BA%8C%E7%BB%B4%E7%A0%81%E7%9B%B8%E5%85%B3%E5%9B%9E%E8%B0%83)

        :param request: Request instance for CreateMultiFlowSignQRCode.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateMultiFlowSignQRCodeRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateMultiFlowSignQRCodeResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateMultiFlowSignQRCode", params, headers=headers)
            response = json.loads(body)
            model = models.CreateMultiFlowSignQRCodeResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateOrganizationBatchSignUrl(self, request):
        """通过此接口，创建企业批量签署链接，企业员工点击链接即可跳转控制台进行批量签署。
        如果没有UserId，Name和Mobile必填，对应的员工必须在企业下已经实名，且该员工为批量签署合同中的签署方。

        :param request: Request instance for CreateOrganizationBatchSignUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateOrganizationBatchSignUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateOrganizationBatchSignUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateOrganizationBatchSignUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CreateOrganizationBatchSignUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreatePersonAuthCertificateImage(self, request):
        """本接口（CreatePersonAuthCertificateImage）用于创建个人用户证书证明图片

        :param request: Request instance for CreatePersonAuthCertificateImage.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreatePersonAuthCertificateImageRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreatePersonAuthCertificateImageResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreatePersonAuthCertificateImage", params, headers=headers)
            response = json.loads(body)
            model = models.CreatePersonAuthCertificateImageResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreatePrepareFlow(self, request):
        """创建快速发起流程
        <br/>适用场景：用户通过API 合同文件及签署信息，并可通过我们返回的URL在页面完成签署控件等信息的编辑与确认，快速发起合同.
        <br/>注：该接口文件的resourceId 是通过上传文件之后获取的。

        :param request: Request instance for CreatePrepareFlow.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreatePrepareFlowRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreatePrepareFlowResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreatePrepareFlow", params, headers=headers)
            response = json.loads(body)
            model = models.CreatePrepareFlowResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreatePreparedPersonalEsign(self, request):
        """本接口（CreatePreparedPersonalEsign）用于创建导入个人印章（处方单场景专用，使用此接口请与客户经理确认）。

        :param request: Request instance for CreatePreparedPersonalEsign.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreatePreparedPersonalEsignRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreatePreparedPersonalEsignResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreatePreparedPersonalEsign", params, headers=headers)
            response = json.loads(body)
            model = models.CreatePreparedPersonalEsignResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateReleaseFlow(self, request):
        """发起解除协议，主要应用场景为：基于一份已经签署的合同(签署流程)，进行解除操作。

        :param request: Request instance for CreateReleaseFlow.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateReleaseFlowRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateReleaseFlowResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateReleaseFlow", params, headers=headers)
            response = json.loads(body)
            model = models.CreateReleaseFlowResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateSchemeUrl(self, request):
        """获取小程序签署链接

        适用场景：如果需要签署人在自己的APP、小程序、H5应用中签署，可以通过此接口获取跳转腾讯电子签小程序的签署跳转链接。

        注：如果签署人是在PC端扫码签署，可以通过生成跳转链接自主转换成二维码，让签署人在PC端扫码签署。


        跳转到小程序的实现，参考官方文档（分为<a href="https://developers.weixin.qq.com/miniprogram/dev/api/navigate/wx.navigateToMiniProgram.html">全屏</a>、<a href="https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/openEmbeddedMiniProgram.html">半屏</a>两种方式）


        如您需要自主配置小程序跳转链接，请参考: <a href="https://cloud.tencent.com/document/product/1323/74774">跳转小程序链接配置说明</a>

        :param request: Request instance for CreateSchemeUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateSchemeUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateSchemeUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateSchemeUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CreateSchemeUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateSeal(self, request):
        """本接口（CreateSeal）用于创建企业电子印章，支持创建企业公章，合同章，财务专用章和人事专用章创建。

        :param request: Request instance for CreateSeal.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateSealRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateSealResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateSeal", params, headers=headers)
            response = json.loads(body)
            model = models.CreateSealResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateSealPolicy(self, request):
        """对企业员工进行印章授权

        :param request: Request instance for CreateSealPolicy.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateSealPolicyRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateSealPolicyResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateSealPolicy", params, headers=headers)
            response = json.loads(body)
            model = models.CreateSealPolicyResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateUserAutoSignEnableUrl(self, request):
        """企业方可以通过此接口获取个人用户开启自动签的跳转链接（处方单场景专用，使用此接口请与客户经理确认）

        :param request: Request instance for CreateUserAutoSignEnableUrl.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateUserAutoSignEnableUrlRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateUserAutoSignEnableUrlResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateUserAutoSignEnableUrl", params, headers=headers)
            response = json.loads(body)
            model = models.CreateUserAutoSignEnableUrlResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def CreateWebThemeConfig(self, request):
        """用来创建页面主题配置

        :param request: Request instance for CreateWebThemeConfig.
        :type request: :class:`tencentcloud.ess.v20201111.models.CreateWebThemeConfigRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.CreateWebThemeConfigResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateWebThemeConfig", params, headers=headers)
            response = json.loads(body)
            model = models.CreateWebThemeConfigResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DeleteIntegrationDepartment(self, request):
        """通过此接口，删除企业的部门。

        :param request: Request instance for DeleteIntegrationDepartment.
        :type request: :class:`tencentcloud.ess.v20201111.models.DeleteIntegrationDepartmentRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DeleteIntegrationDepartmentResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DeleteIntegrationDepartment", params, headers=headers)
            response = json.loads(body)
            model = models.DeleteIntegrationDepartmentResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DeleteIntegrationEmployees(self, request):
        """移除员工
        这里分两个场景
        如果不传交接人的ReceiveUserId或者ReceiveOpenId，则会直接把这个人进行离职
        如果传了交接人，会把离职人未处理完的合同交接给交接人后再离职

        :param request: Request instance for DeleteIntegrationEmployees.
        :type request: :class:`tencentcloud.ess.v20201111.models.DeleteIntegrationEmployeesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DeleteIntegrationEmployeesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DeleteIntegrationEmployees", params, headers=headers)
            response = json.loads(body)
            model = models.DeleteIntegrationEmployeesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DeleteIntegrationRoleUsers(self, request):
        """解绑员工与对应角色关系

        :param request: Request instance for DeleteIntegrationRoleUsers.
        :type request: :class:`tencentcloud.ess.v20201111.models.DeleteIntegrationRoleUsersRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DeleteIntegrationRoleUsersResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DeleteIntegrationRoleUsers", params, headers=headers)
            response = json.loads(body)
            model = models.DeleteIntegrationRoleUsersResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DeleteSealPolicies(self, request):
        """撤销员工持有的印章权限

        :param request: Request instance for DeleteSealPolicies.
        :type request: :class:`tencentcloud.ess.v20201111.models.DeleteSealPoliciesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DeleteSealPoliciesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DeleteSealPolicies", params, headers=headers)
            response = json.loads(body)
            model = models.DeleteSealPoliciesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeExtendedServiceAuthInfos(self, request):
        """查询企业扩展服务授权信息，目前支持查询：企业静默签，企业与港澳台居民签署合同，使用手机号验证签署方身份，骑缝章，批量签署能力是否已经开通

        :param request: Request instance for DescribeExtendedServiceAuthInfos.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeExtendedServiceAuthInfosRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeExtendedServiceAuthInfosResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeExtendedServiceAuthInfos", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeExtendedServiceAuthInfosResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeFileUrls(self, request):
        """查询文件下载URL。
        适用场景：通过传参合同流程编号，下载对应的合同PDF文件流到本地。

        :param request: Request instance for DescribeFileUrls.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeFileUrlsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeFileUrlsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeFileUrls", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeFileUrlsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeFlowBriefs(self, request):
        """查询流程基础信息
        适用场景：可用于主动查询某个合同流程的签署状态信息。可以配合回调通知使用。
        每个企业限制日调用量限制：100W，当日超过此限制后再调用接口返回错误

        :param request: Request instance for DescribeFlowBriefs.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeFlowBriefsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeFlowBriefsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeFlowBriefs", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeFlowBriefsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeFlowComponents(self, request):
        """查询流程填写控件内容，可以根据流程Id查询该流程相关联的填写控件信息和填写内容。

        :param request: Request instance for DescribeFlowComponents.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeFlowComponentsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeFlowComponentsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeFlowComponents", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeFlowComponentsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeFlowEvidenceReport(self, request):
        """查询出证报告，返回报告 URL。出证报告编号通过CreateFlowEvidenceReport接口获取。

        :param request: Request instance for DescribeFlowEvidenceReport.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeFlowEvidenceReportRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeFlowEvidenceReportResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeFlowEvidenceReport", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeFlowEvidenceReportResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeFlowInfo(self, request):
        """查询合同详情
        适用场景：可用于主动查询某个合同详情信息。

        :param request: Request instance for DescribeFlowInfo.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeFlowInfoRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeFlowInfoResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeFlowInfo", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeFlowInfoResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeFlowTemplates(self, request):
        """本接口用于查询本企业模板列表。

        当模板较多或模板中的控件较多时，可以通过查询模板接口更方便的获取模板列表，以及每个模板内的控件信息。

        > **适用场景**
        >
        >  该接口常用来配合“模板发起合同-创建电子文档”接口作为前置的接口使用。
        >  一个模板通常会包含以下结构信息
        >- 模板基本信息
        >- 发起方参与信息Promoter、签署参与方 Recipients，后者会在模板发起合同时用于指定参与方
        >- 填写控件 Components
        >- 签署控件 SignComponents
        >- 生成模板的文件基础信息 FileInfos

        :param request: Request instance for DescribeFlowTemplates.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeFlowTemplatesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeFlowTemplatesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeFlowTemplates", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeFlowTemplatesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeIntegrationDepartments(self, request):
        """通过此接口，查询企业的部门，支持查询单个部门节点或单个部门节点及一级子节点部门列表。

        :param request: Request instance for DescribeIntegrationDepartments.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationDepartmentsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationDepartmentsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeIntegrationDepartments", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeIntegrationDepartmentsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeIntegrationEmployees(self, request):
        """查询企业员工列表，每次返回的数据量最大为20

        :param request: Request instance for DescribeIntegrationEmployees.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationEmployeesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationEmployeesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeIntegrationEmployees", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeIntegrationEmployeesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeIntegrationMainOrganizationUser(self, request):
        """集团企业统一使用主代子进行操作，无需根据子企业账号进行转化查询，该接口需要屏蔽下线

        通过子企业影子账号查询主企业员工账号

        :param request: Request instance for DescribeIntegrationMainOrganizationUser.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationMainOrganizationUserRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationMainOrganizationUserResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeIntegrationMainOrganizationUser", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeIntegrationMainOrganizationUserResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeIntegrationRoles(self, request):
        """分页查询企业角色列表，法人的角色是系统保留角色，不会返回，按照角色创建时间升序排列

        :param request: Request instance for DescribeIntegrationRoles.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationRolesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeIntegrationRolesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeIntegrationRoles", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeIntegrationRolesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeOrganizationGroupOrganizations(self, request):
        """此API接口用户查询加入集团的成员企业

        :param request: Request instance for DescribeOrganizationGroupOrganizations.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeOrganizationGroupOrganizationsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeOrganizationGroupOrganizationsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeOrganizationGroupOrganizations", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeOrganizationGroupOrganizationsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeOrganizationSeals(self, request):
        """查询企业印章的列表，需要操作者具有查询印章权限
        客户指定需要获取的印章数量和偏移量，数量最多100，超过100按100处理；入参InfoType控制印章是否携带授权人信息，为1则携带，为0则返回的授权人信息为空数组。接口调用成功返回印章的信息列表还有企业印章的总数。

        :param request: Request instance for DescribeOrganizationSeals.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeOrganizationSealsRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeOrganizationSealsResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeOrganizationSeals", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeOrganizationSealsResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeThirdPartyAuthCode(self, request):
        """通过AuthCode查询用户是否实名

        :param request: Request instance for DescribeThirdPartyAuthCode.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeThirdPartyAuthCodeRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeThirdPartyAuthCodeResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeThirdPartyAuthCode", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeThirdPartyAuthCodeResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DescribeUserAutoSignStatus(self, request):
        """企业方可以通过此接口查询个人用户自动签开启状态。（处方单场景专用，使用此接口请与客户经理确认）

        :param request: Request instance for DescribeUserAutoSignStatus.
        :type request: :class:`tencentcloud.ess.v20201111.models.DescribeUserAutoSignStatusRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DescribeUserAutoSignStatusResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DescribeUserAutoSignStatus", params, headers=headers)
            response = json.loads(body)
            model = models.DescribeUserAutoSignStatusResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def DisableUserAutoSign(self, request):
        """企业方可以通过此接口关闭个人的自动签功能（处方单场景专用，使用此接口请与客户经理确认）

        :param request: Request instance for DisableUserAutoSign.
        :type request: :class:`tencentcloud.ess.v20201111.models.DisableUserAutoSignRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.DisableUserAutoSignResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("DisableUserAutoSign", params, headers=headers)
            response = json.loads(body)
            model = models.DisableUserAutoSignResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def GetTaskResultApi(self, request):
        """查询转换任务的状态。转换任务Id通过发起转换任务接口（CreateConvertTaskApi）获取。
        注意：大文件转换所需的时间可能会比较长。

        :param request: Request instance for GetTaskResultApi.
        :type request: :class:`tencentcloud.ess.v20201111.models.GetTaskResultApiRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.GetTaskResultApiResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("GetTaskResultApi", params, headers=headers)
            response = json.loads(body)
            model = models.GetTaskResultApiResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def ModifyApplicationCallbackInfo(self, request):
        """新增/删除应用callbackinfo
        callbackinfo包含： 回调地址和签名key
        操作：新增/删除

        :param request: Request instance for ModifyApplicationCallbackInfo.
        :type request: :class:`tencentcloud.ess.v20201111.models.ModifyApplicationCallbackInfoRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.ModifyApplicationCallbackInfoResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ModifyApplicationCallbackInfo", params, headers=headers)
            response = json.loads(body)
            model = models.ModifyApplicationCallbackInfoResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def ModifyIntegrationDepartment(self, request):
        """通过此接口，更新企业的部门信息，支持更新部门名、客户系统部门ID、部门序列号。

        :param request: Request instance for ModifyIntegrationDepartment.
        :type request: :class:`tencentcloud.ess.v20201111.models.ModifyIntegrationDepartmentRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.ModifyIntegrationDepartmentResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ModifyIntegrationDepartment", params, headers=headers)
            response = json.loads(body)
            model = models.ModifyIntegrationDepartmentResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def ModifyIntegrationRole(self, request):
        """此接口（ModifyIntegrationRole）用来更新企业自定义的SaaS角色或集团角色。

        适用场景1：更新当前企业的自定义SaaS角色或集团角色，并且更新时不进行角色中权限的更新（PermissionGroups 参数不传）。

        适用场景2：更新当前企业的自定义SaaS角色或集团角色，并且更新时进行角色中权限的设置（PermissionGroups 参数要传），权限树内容 PermissionGroups 可参考接口 DescribeIntegrationRoles 的输出。
        适用场景3：更新集团角色管理的子企业列表，可通过设置 SubOrganizationIds 参数达到此效果。

        适用场景4：主企业代理子企业操作的场景，需要设置Agent参数，并且ProxyOrganizationId设置为子企业的id即可。

        注意事项：SaaS角色和集团角色对应的权限树是不一样的。

        :param request: Request instance for ModifyIntegrationRole.
        :type request: :class:`tencentcloud.ess.v20201111.models.ModifyIntegrationRoleRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.ModifyIntegrationRoleResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ModifyIntegrationRole", params, headers=headers)
            response = json.loads(body)
            model = models.ModifyIntegrationRoleResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def StartFlow(self, request):
        """此接口用于发起流程
        适用场景：见创建签署流程接口。
        注：该接口是“创建电子文档”接口的后置接口，用于激活包含完整合同信息（模板及内容信息）的流程。激活后的流程就是一份待签署的电子合同。

        :param request: Request instance for StartFlow.
        :type request: :class:`tencentcloud.ess.v20201111.models.StartFlowRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.StartFlowResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("StartFlow", params, headers=headers)
            response = json.loads(body)
            model = models.StartFlowResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def UnbindEmployeeUserIdWithClientOpenId(self, request):
        """将存在绑定关系的电子签系统员工userId与客户系统员工openId进行解绑

        :param request: Request instance for UnbindEmployeeUserIdWithClientOpenId.
        :type request: :class:`tencentcloud.ess.v20201111.models.UnbindEmployeeUserIdWithClientOpenIdRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.UnbindEmployeeUserIdWithClientOpenIdResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("UnbindEmployeeUserIdWithClientOpenId", params, headers=headers)
            response = json.loads(body)
            model = models.UnbindEmployeeUserIdWithClientOpenIdResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def UpdateIntegrationEmployees(self, request):
        """更新员工信息(姓名，手机号，邮件、部门)，用户实名后无法更改姓名与手机号。
        可进行批量操作，Employees中的userID与openID二选一必填

        :param request: Request instance for UpdateIntegrationEmployees.
        :type request: :class:`tencentcloud.ess.v20201111.models.UpdateIntegrationEmployeesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.UpdateIntegrationEmployeesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("UpdateIntegrationEmployees", params, headers=headers)
            response = json.loads(body)
            model = models.UpdateIntegrationEmployeesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def UploadFiles(self, request):
        """此接口（UploadFiles）用于文件上传。<br/>
        适用场景：用于生成pdf资源编号（FileIds）来配合“用PDF创建流程”接口使用，使用场景可详见“用PDF创建流程”接口说明。<br/>

        其中上传的文件，图片类型(png/jpg/jpeg)大小限制为5M，其他大小限制为60M。<br/>
        调用时需要设置Domain/接口请求域名为 file.ess.tencent.cn,代码示例：<br/>
        HttpProfile httpProfile = new HttpProfile();<br/>
        httpProfile.setEndpoint("file.test.ess.tencent.cn");<br/>

        :param request: Request instance for UploadFiles.
        :type request: :class:`tencentcloud.ess.v20201111.models.UploadFilesRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.UploadFilesResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("UploadFiles", params, headers=headers)
            response = json.loads(body)
            model = models.UploadFilesResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))


    def VerifyPdf(self, request):
        """对流程的合同文件进行数字签名验证，判断文件是否被篡改。

        :param request: Request instance for VerifyPdf.
        :type request: :class:`tencentcloud.ess.v20201111.models.VerifyPdfRequest`
        :rtype: :class:`tencentcloud.ess.v20201111.models.VerifyPdfResponse`

        """
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("VerifyPdf", params, headers=headers)
            response = json.loads(body)
            model = models.VerifyPdfResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))