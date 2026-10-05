from openai import AsyncOpenAI, APIConnectionError, APIStatusError, APITimeoutError


class ConfigurationFailure(Exception):
    pass


class ModelFailure(Exception):
    pass


class AzureClient:
    def __init__(self, settings):
        self.settings = settings
        self.client = AsyncOpenAI(base_url=settings.azure_endpoint, api_key=settings.azure_api_key,
                                  max_retries=1, timeout=45)

    async def response(self, **kwargs):
        try:
            response = await self.client.responses.create(model=self.settings.azure_deployment, store=False, **kwargs)
        except APITimeoutError:
            raise ModelFailure('Azure request timed out. Try a shorter recording or retry later.') from None
        except APIConnectionError:
            raise ModelFailure('Could not connect to Azure. Check network connectivity.') from None
        except APIStatusError as exc:
            # Keep provider payloads out of user-visible errors.
            raise ConfigurationFailure(f'Azure rejected the request (HTTP {exc.status_code}). Check configuration or retry later.') from None
        if response.status != 'completed':
            raise ModelFailure('Azure returned an incomplete response. Retry or use a shorter recording.')
        return response

    async def close(self):
        await self.client.close()
