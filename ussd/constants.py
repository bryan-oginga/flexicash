# constants.py

# Welcome messages
WELCOME_MESSAGE_NEW_USER = "CON Welcome to FlexiCash Microfinance. Please select an option:\n1. Register"
WELCOME_MESSAGE_REGISTERED_USER = (
    "CON Welcome back to FlexiCash.\n"
    "1. Apply  Loan\n"
    "2. Repay Loan\n"
    "3. Check Loan Limit\n"
    "4. Request Statement\n"
    "5. Exit"
)

# Repayment options
REPAYMENT_OPTIONS = "CON Please select payment option:\n1. Full Payment\n2. Partial Payment"
REPAYMENT_FULL_PROMPT = "CON Enter your PIN to confirm full repayment."
REPAYMENT_PARTIAL_PROMPT = "CON Enter the amount for partial repayment."

# Statement options
STATEMENT_PERIOD_PROMPT = (
    "CON Please select period:\n"
    "1. 1 Month\n"
    "2. 3 Months\n"
    "3. 6 Months\n"
    "4. 1 Year"
)

# Exit and error messages
EXIT_MESSAGE = "END Thank you for using FlexiCash Microfinance."
INVALID_OPTION = "END Invalid option. Please try again."
# constants.py

# Loan Application Messages
LOAN_TYPE_PROMPT = "CON Please select loan type:\n1. Emergency Loan\n2. Personal Loan\n3. Business Loan"
LOAN_AMOUNT_PROMPT = "CON Enter loan amount:"
PIN_PROMPT = "CON Enter your PIN:"
PIN_CONFIRM_PROMPT = "CON Confirm your PIN:"
AMOUNT_EXCEEDS_LIMIT = "END Requested amount exceeds your loan limit."
ZERO_BALANCE_ERROR = "END You cannot apply for a loan as your balance is zero."
INVALID_AMOUNT_ERROR = "END Please enter a valid numeric amount."
PIN_MISMATCH_ERROR = "END PINs do not match. Please try again."
LOAN_APPLICATION_SUCCESS = "END Loan application submitted successfully."
PENDING_BALANCE_ERROR = "You have a pending loan of {}. Please repay it before applying for a new loan."