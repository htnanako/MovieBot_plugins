import json
import logging

from .DescribeDomainRecords import Sample as AliyunDescribeDomainRecordsSample
from .UpdateDomainRecord import Sample as AliyunUpdateDomainRecordSample

_LOGGER = logging.getLogger(__name__)


def check_record(access_key_id: str,
                 access_key_secret: str,
                 domain_name: str,
                 ):
    RecordResult = AliyunDescribeDomainRecordsSample().main(access_key_id=access_key_id,
                                                            access_key_secret=access_key_secret,
                                                            domain_name=domain_name,
                                                            rr_keyword='@')
    record = RecordResult.body.domain_records.record
    RecordList = []
    for item in record:
        if item.rr != '@':
            continue
        record = {
            'RecordId': item.record_id,
            'RR': item.rr,
            'Type': item.type,
            'DomainName': item.domain_name,
            'Value': item.value,
        }
        RecordList.append(record)
    return json.dumps(RecordList, indent=4, ensure_ascii=False)


def update_record(access_key_id: str,
                  access_key_secret: str,
                  record_id: str,
                  rr: str,
                  record_type: str,
                  value: str
                  ):
    UpdateResult = AliyunUpdateDomainRecordSample().main(access_key_id=access_key_id,
                                                         access_key_secret=access_key_secret,
                                                         record_id=record_id,
                                                         rr=rr,
                                                         record_type=record_type,
                                                         value=value)
    if UpdateResult.status_code == 200:
        return True


def main(access_key_id: str,
         access_key_secret: str,
         domain_name: str,
         now_ip: dict,
         record_type: list):
    RecordList = json.loads(check_record(access_key_id=access_key_id,
                                         access_key_secret=access_key_secret,
                                         domain_name=domain_name))
    update_result = []
    for item in RecordList:
        if item['Type'] == 'A' and 'A' in record_type:
            if item['Value'] != now_ip['ipv4']:
                if update_record(access_key_id=access_key_id,
                                 access_key_secret=access_key_secret,
                                 record_id=item['RecordId'],
                                 rr=item['RR'],
                                 record_type=item['Type'],
                                 value=now_ip['ipv4']):
                    _LOGGER.info(f'当前IPv4地址为{now_ip["ipv4"]}(来源：{now_ip["v4_api"]})')
                    _LOGGER.info(f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv4"]}')
                    update_result.append(f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv4"]}')
            # else:
            #     _LOGGER.info(f'IPv4地址未变化，无需更新')
        elif item['Type'] == 'AAAA' and 'AAAA' in record_type:
            if item['Value'] != now_ip['ipv6']:
                if update_record(access_key_id=access_key_id,
                                 access_key_secret=access_key_secret,
                                 record_id=item['RecordId'],
                                 rr=item['RR'],
                                 record_type=item['Type'],
                                 value=now_ip['ipv6']):
                    _LOGGER.info(f'当前IPv6地址为{now_ip["ipv6"]}(来源：{now_ip["v6_api"]})')
                    _LOGGER.info(f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv6"]}')
                    update_result.append(f'域名{item["RR"]}.{item["DomainName"]}的{item["Type"]}记录已更新为{now_ip["ipv6"]}')
            # else:
            #     _LOGGER.info(f'IPv6地址未变化，无需更新')
    return update_result
