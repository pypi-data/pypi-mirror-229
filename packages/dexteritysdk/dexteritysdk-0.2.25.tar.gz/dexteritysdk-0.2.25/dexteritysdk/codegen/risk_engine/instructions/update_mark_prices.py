# LOCK-BEGIN[imports]: DON'T MODIFY
from .instruction_tag import InstructionTag
from dataclasses import dataclass
from dexteritysdk.codegen.risk_engine.types import UpdateMarkPricesParams
from dexteritysdk.solmate.utils import to_account_meta
from io import BytesIO
from podite import BYTES_CATALOG
from solana.publickey import PublicKey
from solana.transaction import (
    AccountMeta,
    TransactionInstruction,
)
from typing import (
    List,
    Optional,
    Union,
)

# LOCK-END


# LOCK-BEGIN[ix_cls(update_mark_prices)]: DON'T MODIFY
@dataclass
class UpdateMarkPricesIx:
    program_id: PublicKey

    # account metas
    payer: AccountMeta
    mark_prices: AccountMeta
    market_product_group: AccountMeta
    remaining_accounts: Optional[List[AccountMeta]]

    # data fields
    params: UpdateMarkPricesParams

    def to_instruction(self):
        keys = []
        keys.append(self.payer)
        keys.append(self.mark_prices)
        keys.append(self.market_product_group)
        if self.remaining_accounts is not None:
            keys.extend(self.remaining_accounts)

        buffer = BytesIO()
        buffer.write(InstructionTag.to_bytes(InstructionTag.UPDATE_MARK_PRICES))
        buffer.write(BYTES_CATALOG.pack(UpdateMarkPricesParams, self.params))

        return TransactionInstruction(
            keys=keys,
            program_id=self.program_id,
            data=buffer.getvalue(),
        )

# LOCK-END


# LOCK-BEGIN[ix_fn(update_mark_prices)]: DON'T MODIFY
def update_mark_prices(
    payer: Union[str, PublicKey, AccountMeta],
    mark_prices: Union[str, PublicKey, AccountMeta],
    market_product_group: Union[str, PublicKey, AccountMeta],
    params: UpdateMarkPricesParams,
    remaining_accounts: Optional[List[AccountMeta]] = None,
    program_id: Optional[PublicKey] = None,
):
    if program_id is None:
        program_id = PublicKey("92wdgEqyiDKrcbFHoBTg8HxMj932xweRCKaciGSW3uMr")

    if isinstance(payer, (str, PublicKey)):
        payer = to_account_meta(
            payer,
            is_signer=True,
            is_writable=True,
        )
    if isinstance(mark_prices, (str, PublicKey)):
        mark_prices = to_account_meta(
            mark_prices,
            is_signer=False,
            is_writable=True,
        )
    if isinstance(market_product_group, (str, PublicKey)):
        market_product_group = to_account_meta(
            market_product_group,
            is_signer=False,
            is_writable=False,
        )

    return UpdateMarkPricesIx(
        program_id=program_id,
        payer=payer,
        mark_prices=mark_prices,
        market_product_group=market_product_group,
        remaining_accounts=remaining_accounts,
        params=params,
    ).to_instruction()

# LOCK-END
