# Create Vendor Bill Type

## Pre-Condition

- None.

## Flow

1. Open the **Financial Accounting > Configuration > Vendor Bill Types** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Name**: Enter the vendor bill type name.
   - **Code**: Enter a unique code for this type, or fill with **/** to generate it
     later using the **Generate Code** button.
4. Go to the **Accounting** tab and fill in:
   - **Journal**: Select the default journal used when posting a vendor bill of this
     type.
   - **Payable Account**: Select the default payable account used when posting a
     vendor bill of this type.
5. Go to the **Product Configuration** tab and set:
   - **Product Selection Method**: Select how allowed products are determined:
     **Manual**, **Domain** (default), or **Python Code**.
   - **Products**: Only visible when Product Selection Method = **Manual**. Select
     the products allowed on a vendor bill of this type.
   - **Product Domain**: Only visible when Product Selection Method = **Domain**.
     Enter the domain expression evaluated against Product. Default: `[]`.
   - **Product Python Code**: Only visible when Product Selection Method =
     **Python Code**. Enter the Python code that sets the `result` variable to a
     recordset of Product. Default: `result = []`.
6. Go to the **Currency Configuration** tab and set:
   - **Currency Selection Method**: Select how allowed currencies are determined:
     **Manual**, **Domain** (default), or **Python Code**.
   - **Currencies**: Only visible when Currency Selection Method = **Manual**.
     Select the currencies allowed on a vendor bill of this type.
   - **Currency Domain**: Only visible when Currency Selection Method =
     **Domain**. Enter the domain expression evaluated against Currency. Default:
     `[]`.
   - **Currency Python Code**: Only visible when Currency Selection Method =
     **Python Code**. Enter the Python code that sets the `result` variable to a
     recordset of Currency. Default: `result = []`.
7. Go to the **Pricelist Configuration** tab and set:
   - **Pricelist Selection Method**: Select how allowed pricelists are determined:
     **Manual**, **Domain** (default), or **Python Code**.
   - **Pricelists**: Only visible when Pricelist Selection Method = **Manual**.
     Select the pricelists allowed on a vendor bill of this type.
   - **Pricelist Domain**: Only visible when Pricelist Selection Method =
     **Domain**. Enter the domain expression evaluated against Pricelist. Default:
     `[]`.
   - **Pricelist Python Code**: Only visible when Pricelist Selection Method =
     **Python Code**. Enter the Python code that sets the `result` variable to a
     recordset of Pricelist. Default: `result = []`.
8. Click **Save**.

## Post-Condition

- A new Vendor Bill Type record is created and available for selection as **Type**
  on a vendor bill.
