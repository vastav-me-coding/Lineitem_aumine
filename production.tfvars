// config/develop.tfvars
environment         = "production"
app_name = "affinity-ods"
account_id          = "377633137458"
private_subnet_1_name = "AWS-Affinity-US-Prode1-PrivateSubnet1"
private_subnet_0_name = "AWS-Affinity-US-Prode1-PrivateSubnet0"
security_group_web_name = "AWS-Affinity-US-Prode1-AON-WEB-ACCESS"
security_group_app_common_name = "AWS-Affinity-US-Prode1-COMMON-APP-ACCESS"
security_group_db_common_name = "AWS-Affinity-US-Prode1-COMMON-DB-ACCESS"
security_group_db_name = "AWS-Affinity-US-Prode1-AON-DB-ACCESS"
vpc_id              = "vpc-0411cd07123d2ba4d"
region              = "us-east-1"
appid = "AR4262-PR001"

kms_key_id = "b9aebd01-9adb-4288-a192-759ea191b693"
lambda_name = "df-sqs-au-aff-aum-lineitem"
lambda_execution_role_name = "affinity-tds-ar4262-pr001-sqs-lambda-role"
lambda_execution_role_arn = "arn:aws:iam::377633137458:role/app/affinity-tds-ar4262-pr001-sqs-lambda-role"
image_uri = "948273211232.dkr.ecr.us-east-1.amazonaws.com/affinity-ods-ar4262-pr001-df-sqs-au-aff-aum-lineitem:latest"
rds_credentials_secret_arn = "arn:aws:secretsmanager:us-east-1:377633137458:secret:rds-master-credentials-secret-affinity-ods2-Uak2gc"
rds_cluster_endpoint = "affinity-ods2.cluster-cyfwyevzbce3.us-east-1.rds.amazonaws.com"
aumine_aff_credentials_secret_arn = "arn:aws:secretsmanager:us-east-1:377633137458:secret:affinity-tds-ar4262-pr001-audbm-affods-credentials-secret-qelPJX"
aumine_aum_credentials_secret_arn = "arn:aws:secretsmanager:us-east-1:377633137458:secret:affinity-tds-ar4262-pr001-audbm-affods-credentials-secret-qelPJX"
sqs_producer_key_secret_arn = "arn:aws:secretsmanager:us-east-1:377633137458:secret:affinity-tds-ar4262-pr001-tds-sqs-producer-v2-credentials-xfmg2j"
sqs_policy_update_url = "https://5amkhm52vukk7tegrrusuxvbv40inebf.lambda-url.us-east-1.on.aws/policy-update"

deployments = {
    ods_aws_lambda_apis_multiple = {
        blue = {
            enabled = true
            overrides = {
                appid = "AR4262-PR001"
            }
        }
        green = {
            enabled = false
            overrides = {
                appid = "AR4262-PR002"
            }
        }
    }
}