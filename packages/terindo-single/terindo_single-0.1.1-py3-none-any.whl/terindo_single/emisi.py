import requests
import json
from requests.adapters import HTTPAdapter
from urllib3 import Retry

class EmisiChecker:
    def __init__(self, dlh_url, dlh_username, dlh_password):
        self.dlh_url = dlh_url
        self.dlh_username = dlh_username
        self.dlh_password = dlh_password
        self.session = self._create_session()

    def _create_session(self):
        """
        Creates a new session with the server.

        :return: The created session object.
        """
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
        }
        retry = Retry(connect=1, backoff_factor=0.1)
        adapter = HTTPAdapter(max_retries=retry)
        s = requests.Session()
        s.mount('https://', adapter)
        s.headers = headers
        s.auth = (self.dlh_username, self.dlh_password)
        return s

    def _fetch_emission_data(self, nopol, timeout=2):
        """
        Fetches emission data from the specified URL.

        Args:
            nopol (str): The parameter used to fetch data from the URL.
            timeout (int, optional): The timeout value for the HTTP request. Defaults to 2.

        Returns:
            dict: The JSON response data from the HTTP request.
        """
        try:
            response = self.session.get(self.dlh_url + nopol, verify=False, timeout=timeout)  # Disabling certificate verification and setting timeout
            response.raise_for_status()  # Raise HTTPError for bad requests
            response_data = response.json()
            return response_data
        except requests.exceptions.RequestException as e:
            print("Error fetching emission data:", e)
            return False, None, None, None

    def emisi(self, nopol, timeout=2):
        """
        Fetches emission data for a vehicle based on its license plate number.
        
        :param nopol: The license plate number of the vehicle.
        :param timeout: The timeout value for the request in seconds (default is 2).
        :return: A tuple containing the following information:
                 - status_check: A boolean indicating whether the emission data was fetched successfully.
                 - nopol: The license plate number of the vehicle.
                 - emisi_status2: The emission status of the vehicle.
                 - emisi_tanggal: The expiration date of the emission test.
                 - jenis_kendaraan: The type of the vehicle.
        """
        
        status_check = False
        emisi_status2 = "error"
        emisi_tanggal = ""
        jenis_kendaraan = ""
        
        try:
            datax = self._fetch_emission_data(nopol, timeout)
            # print(f"datax: {datax}")
            if datax:
                if 'results' in datax and len(datax['results']) > 0:
                    emisi_status2 = datax['results'][0]['status_lulus2']
                    emisi_tanggal = datax['results'][0]['berlaku_sampai'].split(" ")[0]
                    jenis_kendaraan = datax['results'][0]['nama_tipe']
                    status_check = True
                else:
                    emisi_status2 = ""
                    emisi_tanggal = ""
                    jenis_kendaraan = ""
                    status_check = False
                
            else:
                emisi_status2 = "error"
                emisi_tanggal = ""
                jenis_kendaraan = ""
                status_check = False
            
            # print(f"status_emisi_check: {status_check}")
            return status_check, nopol, emisi_status2, emisi_tanggal, jenis_kendaraan
        
        except requests.Timeout:
            print("Timeout fetching emission data")
            status_check, nopol, emisi_status2, emisi_tanggal, jenis_kendaraan
            
        except Exception as e:
            print("Error fetching emission data:", e)
            status_check, nopol, emisi_status2, emisi_tanggal, jenis_kendaraan