terraform {
  backend "s3" {
    encrypt = true
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "< 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

module "ods_aws_lambda_apis_multiple" {
  source = "git::https://gitlab.com/aon/affinity/ods/ods_gitlabterraformmodules.git//modules/module-factory"

  module_name = "ods-aws-lambda-api"
  
  config = {
    app_name = "affinity-tds"
    project = "affinity-tds"
    account_id = var.account_id
    region = var.region
    appid = var.appid
    environment = var.environment

    create_lambda_role = false
    create_ecr_repositories = false
    create_lambdas = true
    create_apis = false
    create_public_apis = false
    create_api_authorizers = false
    create_sqs_lambda_role = false
    create_sqs_queues = true

    ecr_repository_names = []
    kms_key_id = var.kms_key_id
    
    // lambdas
    lambdas = {
      "df-sqs-au-aff-aum-lineitem" = {
        image_uri = var.image_uri
        timeout = 900
        memory_size = 2048
        lambda_execution_role_name = var.lambda_execution_role_name
        environment_variables = {
          RDS_SECRETS_MANAGER_ID = var.rds_credentials_secret_arn
          RDS_DB_NAME = "pnc_warehouse"
          RDS_RAW_DB_NAME = "mdm_raw"
          RDS_REFINED_DB_NAME = "mdm_refined"
          RDS_HOST = var.rds_cluster_endpoint
          AUMINE_AFF_SECRETS_MANAGER_ID = var.aumine_aff_credentials_secret_arn
          AUMINE_AUM_SECRETS_MANAGER_ID = var.aumine_aum_credentials_secret_arn
          SQS_PRODUCER_SECRET_ID = var.sqs_producer_key_secret_arn
          SQS_POLICY_UPDATE_URL = var.sqs_policy_update_url
        }
        vpc_config = {
          security_group_names = tolist([var.security_group_web_name, var.security_group_app_common_name, var.security_group_db_common_name, var.security_group_db_name])
          subnet_names = tolist([var.private_subnet_0_name])
          vpc_id = var.vpc_id
        }
        sqs = {
          kms_data_key_reuse_period_seconds = 300
          visibility_timeout_seconds = 900
          delay_seconds = 0
        }        
      }
    }
    
    // apis
    apis = {}
  }

  deployments = lookup(var.deployments, "ods_aws_lambda_apis_multiple", {
    blue = { 
      enabled = true
      overrides = {
        appid = "AR4262"
      }
    }
  })
}

output "lambda_function_names" {
  value = module.ods_aws_lambda_apis_multiple.lambda_function_names
}