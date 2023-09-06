## Duke.ai Lib (*dukeai_lib*)

Latest Release: 2023-07-25

---

*The dukeai_lib PIP package repository; Contains base functions that are used across multiple internal backend projects making it easier for developers to maintain consistency via a centralized codebase while enabling retroactive updates to core functionality.*

---
**Modules**

- **tools**

   - gen_random_sha()

- **application**

   - check_access()
   - api_response()

- **utilities**

   - DecimalEncoder(class)

- **schema_kung_fu**

  - rate_confirmation
     - *flatten_ratecon()*
     - *unflatten_ratecon()*
  - accessorial
     - *flatten_accessorial()*
     - *unflatten_accessorial()*
  - bill_of_lading
     - *flatten_bol()*
     - *unflatten_bol()*
  - invoice
     - *flatten_invoice()*
     - *unflatten_invoice()*
  - noa_lor
     - *flatten_noa_lor()*
     - *unflatten_noa_lor()*
  - classification
     - *dt_multiclass_to_dynamoson()*
     - *translate_dt_multiclass()*
     - *classification_template()*
     - *standardize_classification_name()*
     - *parse_classification_dynamoson()*
     - *parse_multiple_classification_dynamoson()*
  - schema_utilities
     - *dict(REFERENCE_OPTIONS)*
     - *dict(STATES)*
     - *get_idtype()*
     - *format_state()*
     - *parse_incoming_address()*
     - *format_time()*
     - *parse_time()*
---

**Usage**

pip install dukeai_lib

*and subsequently...*

import dukeai_lib

***or***

from dukeai_lib.schema_kung_fu import schema_utilities