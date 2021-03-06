import hashlib, csv
from apps.requests.models import *
from logging.logger import main_logger_path, main_logger_headers


dupe_id_file_path = '/home/ubuntu/foiamachine/repo/foiamachine/matt_utils/logging/logs/dupe_att_ids.txt'


def get_attachments():
    dd_atts = get_deduped_attachments()
    return get_unprocessed_attachments(dd_atts)

def get_deduped_attachments():
    """
    returns attachments
    after checksum confirms they're
    deduplicated
    """
    dupe_ids = []
    # id: hash dict may be useful for debugging
    dupe_id_file= open(dupe_id_file_path,'w')
    all_attachments = []
    all_hashes = []
    for att in Attachment.objects.all():
        hash_str = hashlib.md5(open(att.file.path).read()).hexdigest()
        # skip dupes
        if hash_str in all_hashes:
            dupe_id_file.write(str(att.id) + '\n')
            continue
        else:
            all_attachments.append(att)
            all_hashes.append(hash_str)
    dupe_id_file.close()
    return all_attachments


def get_unprocessed_attachments(atts):
    main_log = open(main_logger_path,'r')
    main_log_csv = csv.DictReader(main_log, main_logger_headers)
    processed_ids = [x['attachment_id'] for x in main_log_csv if x['processed'] == 'True']
    main_log.close()
    return [att for att in atts if att.id not in processed_ids]
