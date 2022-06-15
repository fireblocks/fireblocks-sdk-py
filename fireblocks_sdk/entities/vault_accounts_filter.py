from typing import Union
from urllib import parse

FilterParamType = Union[str, None]


class VaultAccountsFilter:
    def __init__(self, name_prefix: FilterParamType, name_suffix: FilterParamType,
                 min_amount_threshold: FilterParamType, asset_id: FilterParamType) -> None:
        self.name_prefix = name_prefix
        self.name_suffix = name_suffix
        self.min_amount_threshold = min_amount_threshold
        self.asset_id = asset_id

    def serialize(self) -> str:
        params = {}
        if self.name_prefix:
            params.update({'namePrefix': self.name_prefix})
        if self.name_suffix:
            params.update({'nameSuffix': self.name_suffix})
        if self.min_amount_threshold:
            params.update({'minAmountThreshold': self.min_amount_threshold})
        if self.asset_id:
            params.update({'assetId': self.asset_id})

        return parse.urlencode(params)
