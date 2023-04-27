Recatizer
---
Lost pet search service. The project is frozen.
 
Scenarios
---
Use cases:


![use_cases.png](docs/pics/use_cases.png) 

For each use case you have to upload information about the lost cat 
(for each use case):

![cat_info.png](docs/pics/cat_info.png)

Stack and system design
---

![system_design.png](docs/pics/system_design.png)
**Stack**: 
- Kafka, 
-  MongoDB, 
-  Redis, 
-  Yandex Cloud:
   - Yandex Object Storage (S3 type storage), 
   - Yandex Cloud Function (Serverless Function), 
   - Yandex Compute Cloud (VM),
- aiogramm.

**Inference:**
![infirence.png](docs/pics/inference.png)









