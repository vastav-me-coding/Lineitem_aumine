// config/develop.tfvars
environment         = "staging"
app_name = "affinity-ods"
project = "affinity-ods"
account_id          = "948273211232"
private_subnet_0_name = "AWS-Affinity-US-Staginge1-PrivateSubnet0"
security_group_web_name = "AWS-Affinity-US-Staginge1-AON-WEB-ACCESS"
security_group_app_common_name = "AWS-Affinity-US-Staginge1-COMMON-APP-ACCESS"
security_group_db_common_name = "AWS-Affinity-US-Staginge1-COMMON-DB-ACCESS"
security_group_db_name = "AWS-Affinity-US-Staginge1-AON-DB-ACCESS"
vpc_id              = "vpc-0fe42a8cd01d709d0"
region              = "us-east-1"

kms_key_id = "046f32d9-58c4-4c5c-b44d-5605e9fdbccd"
lambda_name = "df-sqs-au-aff-aum-lineitem"
lambda_execution_role_name = "affinity-tds-ar4262-sg001-sqs-lambda-role"
lambda_execution_role_arn = "arn:aws:iam::948273211232:role/app/affinity-tds-ar4262-sg001-sqs-lambda-role"
image_uri = "948273211232.dkr.ecr.us-east-1.amazonaws.com/affinity-ods-ar4262-sg001-df-sqs-au-aff-aum-lineitem:latest"
rds_credentials_secret_arn = "arn:aws:secretsmanager:us-east-1:948273211232:secret:rds-master-credentials-secret-affinity-ods2-staging-E2YKEk"
rds_cluster_endpoint = "affinity-ods2-staging.cluster-csllwxc3aae4.us-east-1.rds.amazonaws.com"
aumine_aff_credentials_secret_arn = "arn:aws:secretsmanager:us-east-1:948273211232:secret:affinity-tds-ar4262-sg001-audbm-affods-credentials-secret-OZQMaS"
aumine_aum_credentials_secret_arn = "arn:aws:secretsmanager:us-east-1:948273211232:secret:affinity-tds-ar4262-sg001-audbm-affods-credentials-secret-OZQMaS"
sqs_producer_key_secret_arn = "arn:aws:secretsmanager:us-east-1:948273211232:secret:affinity-tds-ar4262-sg001-tds-sqs-producer-v2-credentials-CGQZA5"
sqs_policy_update_url = "https://dghqwaqraa4efkwwxgmzdx2jei0qcvgo.lambda-url.us-east-1.on.aws/policy-update"

deployments = {
    ods_aws_lambda_apis_multiple = {
        blue = {
            enabled = true
            overrides = {
                appid = "AR4262-SG001"
            }
        }
        green = {
            enabled = false
            overrides = {
                appid = "AR4262-SG002"
            }
        }
    }
}
