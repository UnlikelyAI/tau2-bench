from pathlib import Path
from loguru import logger
from tau2.utils.utils import DATA_DIR

FINANCIAL_ADVICE_DATA_DIR = DATA_DIR / "tau2" / "domains" / "financial-advice"
FINANCIAL_ADVICE_POLICY_PATH = FINANCIAL_ADVICE_DATA_DIR / "policy.md"
FINANCIAL_ADVICE_TASK_SET_PATH = FINANCIAL_ADVICE_DATA_DIR / "tasks.json"
KNOWLEDGE_BASE_PATH = FINANCIAL_ADVICE_DATA_DIR / "knowledge_base_md"
PRODUCT_FILES = [
    # Ready-Made Investment ISA / Ready-Made Investment Account
    "investing/text/ready-made-investments.md",
    "investing/pdf/ready-made-investments-kfd-isa-17998217.md",
    "investing/pdf/ready-made-investments-kfd-gia-a7478096.md",
    "investing/pdf/rmi-fund-range-711f7e2c.md",
    # Share Dealing ISA / Share Dealing Account
    "investing/text/share-dealing-isa.md",
    "investing/text/share-dealing-account.md",
    "investing/text/share-dealing-services.md",
    "investing/text/charges.md",
    "investing/text/ways-to-invest.md",
    "investing/text/what-is-a-stocks-and-shares-isa.md",
    # Investment taxes
    "investing/text/tax-changes.md",
    "investing/text/tax-efficient-investing.md",
    # Cash ISA (incl. Fixed-Rate Cash ISA)
    "savings/text/isas-explained.md",
    "savings/text/fixed-rate.md",
    "savings/text/savings.md",
    "savings/text/fixed-rate-maturity.md",
    "savings/text/isa-top-up.md",
    "savings/text/isa-allowance.md",
    # Easy Saver
    "savings/text/easy-saver.md",
    # Monthly Saver
    "savings/text/monthly-saver.md",
    # Online Fixed Bond
    "savings/text/online-fixed-bonds.md",
]


def load_product_file_contents(kb_path: Path, product_files: list[str]) -> list[str]:
    product_file_contents = []
    for f in product_files:
        file_path = kb_path / f
        if not file_path.exists():
            logger.error(f"Could not find product file: {file_path}")
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                product_file_contents.append(f.read())
    logger.info(f"Loaded {len(product_file_contents)} product files")
    return product_file_contents