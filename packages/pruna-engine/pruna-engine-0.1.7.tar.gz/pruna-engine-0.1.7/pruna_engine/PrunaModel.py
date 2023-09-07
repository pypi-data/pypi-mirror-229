import requests
import torch
import time


class PrunaModel:
    def __init__(self, model, api_key, verify_url):
        self.__model = model
        self.__checkn = 0
        self.__checkevery = 100
        self.__time_elapsed = time.time()
        self.api_key = api_key
        self.verify_url = verify_url

    def __call__(self, *input_data, **kwargs):
        # Increment checkn
        self.__checkn += 1

        # Verify the API key
        if self.__checkn == 1 or self.__checkn % self.__checkevery == 0:
            MAX_RETRIES = 3
            RETRY_DELAY = 5  # time in seconds

            for retry in range(MAX_RETRIES):
                try:
                    response = requests.post(
                        self.verify_url,
                        data={
                            'api_key': self.api_key,
                            'number_of_inferences': self.__checkn if self.__checkn == 1 else self.__checkevery,
                            'time_elapsed': time.time() - self.__time_elapsed}
                    )
                    response.raise_for_status()
                    json_response = response.json()
                    if json_response.get('status') != 'Allowed':
                        raise Exception('API key verification failed or prediction limit reached')
                    else:
                        self.__time_elapsed = time.time()
                        break  # success, so exit the loop

                except requests.exceptions.HTTPError as e:
                    if response.status_code == 500 and retry < MAX_RETRIES - 1:  # Check if it's a 500 error and not the last retry
                        print(f"Received a 500 error, retrying in {RETRY_DELAY} seconds...")
                        time.sleep(RETRY_DELAY)
                    else:
                        raise SystemExit(e)

        # If the API key is valid and hasn't exceeded the limit, make the prediction
        with torch.no_grad():
            return self.__model(*input_data, **kwargs)

    def __getattr__(self, attr):
        # Forward the attribute access to __model
        return getattr(self.__model, attr)
