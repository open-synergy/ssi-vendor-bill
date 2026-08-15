# Create Vendor Bill

> **Module:** ssi_vendor_bill\
> **Model:** `vendor_bill`\
> **Menu:** Financial Accounting > Account Payable > Vendor Bill\
> **Actor:** user in group `Vendor Bill / User`\
> **State:** `—` → `draft`

## Pre-Condition

- None.

## Flow

1. Open the **Financial Accounting > Account Payable > Vendor Bill** menu.
2. Click the **New** button. **(14.0: "Create")**
3. Fill in the required fields:
   - **Type**: Select the vendor bill type. It determines the default Journal and
     Payable Account, and limits the Currency, Pricelist, and products allowed on this
     document.
   - **Partner**: Select the vendor this bill is issued to.
   - **Date**: Accounting date of the document. Defaults to today. Change if needed.
   - **Date Due**: Due date of the payable. Automatically filled if **Duration** is
     selected. Change if needed.
   - **Currency**: Automatically limited to the currencies allowed by the selected
     **Type**.
   - **Pricelist**: Automatically limited to the pricelists allowed by the selected
     **Type**.
   - **Journal**: Automatically filled from **Type**. Change if needed.
   - **Payable Account**: Automatically filled from **Type**. Change if needed.
4. Optionally fill in the other fields available in Draft status:
   - **Vendor Document Number**: Reference number of the original document issued by the
     vendor (e.g. their own invoice number).
   - **Duration**: Select a predefined duration to automatically calculate **Date Due**
     from **Date**.
   - **Analytic Account**: Select the analytic account used to track the cost of this
     document.
5. On the **Detail** tab, add lines describing the products/services being billed.
   Repeat the following steps as many times as needed:
   - Click **Add a line**.
   - Fill in each line with:
     - **Product**: Select the product/service being billed.
     - **Description**: Automatically filled from **Product**. Change if needed.
     - **Usage**: Select the usage that determines the default **Account** and
       **Tax(es)** for this line.
     - **Account**: Automatically filled from **Product** and **Usage**. Change if
       needed.
     - **Analytic Account**: Optionally select the analytic account for this line.
     - **UoM**: Automatically filled from **Product**. Change if needed.
     - **Quantity**: Enter the quantity being billed.
     - **Price Unit**: Automatically filled from **Product**, **Pricelist**,
       **Quantity**, and **UoM**. Change if needed.
     - **Tax(es)**: Automatically filled from **Product** and **Usage**. Change if
       needed.
6. Click **Save**.

## Post-Condition

- A new record is created in **Draft** status.
- The document number is displayed as **/** until the record reaches the **Unpaid**
  status.
