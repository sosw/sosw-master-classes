# FaaS Fundamentals - Agenda

| **Name** | **Activity Type** | **Time** |
| ---| ---| --- |
| Students Introduction | Interactive | 15 |
| What is Cloud | Lecture | 5 |
| Virtualization Fundamentals (Schema) | Lecture | 30 |
|  |  |  |
| AWS Web Console Overview | Demo | 5 |
| AWS IAM Users, Groups, Roles, Policies | Lecture | 10 |
| AWS IAM Add Users for Attendees | Demo | 10 |
| Coffee break |  | 15 |
|  |  |  |
| FaaS Fundamentals (Schema) | Lecture | 30 |
| Tasks Overview | Practice | 10 |
| AWS Lambda Deploy (SAM or Web GUI) | Practice | 15 |
| AWS Role with iam:ListUsers | Practice | 10 |
| AWS Lambda to return current users | Practice | 5 |
|  |  |  |
| SOSW Course Introduction | Lecture | 15 |
|  |  |  |
| Check Results and Approve PRs | Practice | ∞ |

## AWS Credentials

*   Account: `123456789000`
*   IAM User: `YOUR_NAME`


## Tasks

*   Log in to console
*   Find and observe IAM users
*   Create function YOUR\_NAME\_list\_users (return just "Hello world")
*   Find command in the SDK to show users from IAM
*   Implement it in your function
*   Fix the permissions problem
*   Add a public function HTTP endpoint
*   Don't do this in production

## Extra

*   Fork repository: [https://github.com/sosw/sosw-master-classes](https://github.com/sosw/sosw-master-classes)
*   Commit your function code to your fork in: `results/YOUR_NAME/YOUR_NAME_list_users.[py]`

*   Make a PR from your fork to the Git upstream
*   Deploy function with AWS SAM.
*   Commit `results/YOUR_NAME/template.yaml`
