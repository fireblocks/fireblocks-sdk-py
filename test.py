from fireblocks_sdk import FireblocksSDK
import json
from fireblocks_sdk.api_types import DestinationTransferPeerPath, TransferPeerPath, VAULT_ACCOUNT

privateKey = open('/home/snir/WorkSpace/Fireblocks/api/tc/api-test-client/KEYS/env.key', 'r').read()
apiKey = '5ceccfa6-030c-53a5-90a2-507cae73bab8'
fireblocks = FireblocksSDK(privateKey, apiKey,'https://dev2-developer-api.waterballoons.xyz')



res = fireblocks.get_vault_accounts(name_suffix='t')


print(res)

