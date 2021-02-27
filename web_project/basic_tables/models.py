from django.db import models

app_name = "basic_tables"


class InputData(models.Model):
    # 加一个字段 记录是否能正常写入
    test_model = models.CharField(max_length=100, null=True)
    type_of_test = models.CharField(max_length=100, null=True)
    details = models.CharField(max_length=200, null=True)
    region = models.CharField(max_length=20)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    person_day = models.CharField(max_length=20)
    remark = models.CharField(max_length=100, null=True)
    engineer = models.CharField(max_length=100, null=True)
    update_reason = models.TextField(null=True)
    platform_info = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=100, null=True)
    bpm_link = models.CharField(max_length=100, null=True)


class BasicCountry(models.Model):
    # 基础国家表,手动维护
    country_cn = models.CharField(max_length=30, primary_key=True)
    country_en = models.CharField(max_length=4, null=True)


class UndertakeTeam(models.Model):
    # 测试的承接团队
    country_cn = models.CharField(max_length=30)
    undertake_team = models.CharField(max_length=200, null=True)
    undertake_date = models.DateField(null=True)

    class Meta:
        unique_together = ('country_cn', 'undertake_team', 'undertake_date')


class TestModule(models.Model):
    # 测试的业务模块
    module_name = models.CharField(max_length=100, primary_key=True)
