import json
import logging

from .DescribeRecordList import Sample as TencentDescribeRecordListSample
from .ModifyRecord import Sample as TencentModifyRecordSample

_LOGGER = logging.getLogger(__name__)


def check_record(SecretId: str,
                 SecretKey: str,
                 domain_name: str, ):
    RecordResult = TencentDescribeRecordListSample().main(SecretId=SecretId,
                                                          SecretKey=SecretKey,
                                                          Domain_name=domain_name,
                                                          Subdomain='@')
    RecordList = []
    for item in RecordResult['RecordList']:
        if item['Name'] != '@':
            continue
        record = {
            'RecordId': item['RecordId'],
            'SubDomain': item['Name'],
            'Type': item['Type'],
            'Value': item['Value'],
        }
        RecordList.append(record)
    return json.dumps(RecordList, indent=4, ensure_ascii=False)


def update_record(SecretId: str,
                  SecretKey: str,
                  Domain_name: str,
                  record_id: int,
                  SubDomain: str,
                  record_type: str,
                  value: str
                  ):
    UpdateResult = TencentModifyRecordSample().main(SecretId=SecretId,
                                                    SecretKey=SecretKey,
                                                    Domain_name=Domain_name,
                                                    RecordId=record_id,
                                                    SubDomain=SubDomain,
                                                    RecordType=record_type,
                                                    Value=value)
    if UpdateResult['RequestId']:
        return True


def main(SecretId: str,
         SecretKey: str,
         domain_name: str,
         now_ip: dict,
         record_type: list):
    RecordList = json.loads(check_record(SecretId=SecretId,
                                         SecretKey=SecretKey,
                                         domain_name=domain_name))
    update_result = []
    for item in RecordList:
        if item['Type'] == 'A' and 'A' in record_type:
            if item['Value'] != now_ip['ipv4']:
                if update_record(SecretId=SecretId,
                                 SecretKey=SecretKey,
                                 Domain_name=domain_name,
                                 record_id=item['RecordId'],
                                 SubDomain=item['SubDomain'],
                                 record_type=item['Type'],
                                 value=now_ip['ipv4']):
                    _LOGGER.info(f'当前IPv4地址为{now_ip["ipv4"]}(来源：{now_ip["v4_api"]})')
                    _LOGGER.info(f'域名{item["SubDomain"]}.{domain_name}的{item["Type"]}记录已更新为{now_ip["ipv4"]}')
                    update_result.append(
                        f'域名{item["SubDomain"]}.{domain_name}的{item["Type"]}记录已更新为{now_ip["ipv4"]}')
            # else:
            #     _LOGGER.info(f'IPv4地址未变化，无需更新')
        elif item['Type'] == 'AAAA' and 'AAAA' in record_type:
            if item['Value'] != now_ip['ipv6']:
                if update_record(SecretId=SecretId,
                                 SecretKey=SecretKey,
                                 Domain_name=domain_name,
                                 record_id=item['RecordId'],
                                 SubDomain=item['SubDomain'],
                                 record_type=item['Type'],
                                 value=now_ip['ipv6']):
                    _LOGGER.info(f'当前IPv6地址为{now_ip["ipv6"]}(来源：{now_ip["v6_api"]})')
                    _LOGGER.info(f'域名{item["SubDomain"]}.{domain_name}的{item["Type"]}记录已更新为{now_ip["ipv6"]}')
                    update_result.append(
                        f'域名{item["SubDomain"]}.{domain_name}的{item["Type"]}记录已更新为{now_ip["ipv6"]}')
            # else:
            #     _LOGGER.info(f'IPv6地址未变化，无需更新')
    return update_result
