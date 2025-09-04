variable "account_id" {
  type = string
}

variable "region" {
  type    = string
}

variable "vpc_id" {
  type = string
}

variable "kms_key_id" {
  type = string
}

variable "security_group_web_name" {
  type = string
}

variable "lambda_execution_role_name" {
  type = string
}

variable "lambda_execution_role_arn" {
  type        = string
}

variable "security_group_app_common_name" {
  type    = string
}

variable "security_group_db_common_name" {
  type    = string
}

variable "security_group_db_name" {
  type    = string
}

variable "private_subnet_0_name" {
    type = string
}

variable "lambda_name" {
  type = string
  default = "data-api-retail-broker-contact"
}

variable "image_uri" {
  type = string
}

variable "rds_credentials_secret_arn" {
  type = string
}

variable "rds_cluster_endpoint" {
  type = string
}

variable "aumine_aff_credentials_secret_arn" {
  type = string
}

variable "aumine_aum_credentials_secret_arn" {
  type = string
}

variable "sqs_producer_key_secret_arn" {
  type = string
}

variable "sqs_policy_update_url" {
  type = string
}

variable "api_name" {
  type = string
  default = "retail-broker-contact"
}

variable "environment" {
  type    = string
}

variable "project" {
  type    = string
  default = "affinity-ods"
}

variable "appid" {
  type    = string
  default = "AR4262"
}

variable "bu" {
  type    = string
  default = "Affinity"
}

variable "busub" {
  type    = string
  default = "Affinity"
}

variable "app_name" {
  type    = string
  default = "affinity-ods"
}

variable "owner" {
  type    = string
  default = "Affinity"
}

variable "gitlab_terraform_modules_repo" {
  type = string
  default = "gitlab.com/aon/affinity/ods/ods_gitlabterraformmodules.git"
}

variable "deployments" {
  type = any
}