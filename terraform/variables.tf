variable "yandex_token" {
    description = "Yandex Cloud IAM token"
    type        = string
    sensitive   = true
}

variable "cloud_id" {
    description = "Yandex Cloud ID"
    type        = string
}

variable "folder_id" {
    description = "Yandex Cloud Folder ID"
    type        = string
}

variable "pg_password" {
    description = "PostgreSQL password"
    type        = string
    sensitive   = true
}