import uuid
import hashlib
import datetime
from common.aes_encrypt import get_aes
from TTS.utils.AEScoder import PrpCrypt 

class LicenseHelper(object):
    def generate_license(self, end_date, mac_addr):
        print("Received end_date: {}, mac_addr: {}".format(end_date, mac_addr))
        psw = self.hash_msg('smartant' + str(mac_addr))
        license_str = {}
        license_str['mac'] = mac_addr
        license_str['time_str'] = end_date
        license_str['psw'] = psw
        s = str(license_str)
        licence_result = get_aes().encrypt(s)
        return licence_result
        
    def get_mac_address(self):
        mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
        return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])
        
    def hash_msg(self, msg):
        sha256 = hashlib.sha256()
        sha256.update(msg.encode('utf-8'))
        res = sha256.hexdigest()
        return res
        
    def read_license(self, license_result):
        lic_msg = bytes(license_result, encoding="utf8")
        pc = PrpCrypt('neonneonneonneon')
        license_str = pc.decrypt(lic_msg)
        license_dic = eval(license_str)
        return license_dic
        
    def check_license_date(self, lic_date):
        current_time = datetime.datetime.strftime(datetime.datetime.now() ,"%Y-%m-%d %H:%M:%S")
        current_time_array = datetime.datetime.strptime(current_time,"%Y-%m-%d %H:%M:%S")
        lic_date_array = datetime.datetime.strptime(lic_date, "%Y-%m-%d %H:%M:%S")
        remain_days = lic_date_array - current_time_array
        remain_days = remain_days.days
        if remain_days < 0 or remain_days == 0:
            return False
        else:
            return True
            
    def check_license_psw(self, psw):
        mac_addr = self.get_mac_address()
        hashed_msg = self.hash_msg('smartant' + str(mac_addr))
        if psw == hashed_msg:
            return True
        else:
            return False