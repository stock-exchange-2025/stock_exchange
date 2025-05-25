terraform {
    required_providers {
        yandex = {
            source = "yandex-cloud/yandex"
        }
    }
    required_version = ">= 0.13"
}

provider "yandex" {
    zone = "ru-central1-d"
    token     = var.yandex_token
    cloud_id  = var.cloud_id
    folder_id = var.folder_id
}

resource "yandex_vpc_network" "network" {
    name = "stock-exchange-network"
}

resource "yandex_vpc_subnet" "subnet" {
    name           = "stock-exchange-subnet"
    zone           = "ru-central1-d"
    network_id     = yandex_vpc_network.network.id
    v4_cidr_blocks = ["10.0.0.0/24"]
}

resource "yandex_vpc_security_group" "k8s" {
    name        = "k8s-security-group"
    network_id  = yandex_vpc_network.network.id

    ingress {
        protocol       = "TCP"
        port           = 6443
        v4_cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        protocol       = "TCP"
        port           = 80
        v4_cidr_blocks = ["0.0.0.0/0"]
    }

    ingress {
        protocol       = "TCP"
        port           = 443
        v4_cidr_blocks = ["0.0.0.0/0"]
    }
}

resource "yandex_vpc_security_group" "pg" {
    name        = "pg-security-group"
    network_id  = yandex_vpc_network.network.id

    ingress {
        protocol       = "TCP"
        port           = 6432
        v4_cidr_blocks = ["10.0.0.0/24"]
    }
}

resource "yandex_mdb_postgresql_cluster" "stock-exchange-db" {
    name        = "stock-exchange-db"
    environment = "PRODUCTION"
    network_id  = yandex_vpc_network.network.id
    folder_id   = var.folder_id

    config {
        version = "13"
        resources {
            resource_preset_id = "s2.micro"
            disk_type_id       = "network-ssd"
            disk_size          = 20
        }
    }

    database {
        name       = "hello_fastapi_dev"
        owner      = "hello_fastapi"
    }

    user {
        name     = "hello_fastapi"
        password = var.pg_password
    }

    host {
        zone      = "ru-central1-d"
        subnet_id = yandex_vpc_subnet.subnet.id
    }

    security_group_ids = [yandex_vpc_security_group.pg.id]
}

resource "yandex_iam_service_account" "k8s-sa" {
    description = "Service account for the Kubernetes cluster"
    name        = "k8s-sa"
}

resource "yandex_resourcemanager_folder_iam_binding" "k8s-clusters-agent" {
    folder_id = var.folder_id
    role      = "k8s.clusters.agent"

    members = [
        "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
    ]
}

resource "yandex_resourcemanager_folder_iam_binding" "vpc-public-admin" {
    folder_id = var.folder_id
    role      = "vpc.publicAdmin"

    members = [
        "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
    ]
}

resource "yandex_resourcemanager_folder_iam_binding" "images-puller" {
    folder_id = var.folder_id
    role      = "container-registry.images.puller"

    members = [
        "serviceAccount:${yandex_iam_service_account.k8s-sa.id}"
    ]
}

resource "yandex_kubernetes_cluster" "stock-exchange-k8s" {
    name        = "stock-exchange-k8s"
    network_id  = yandex_vpc_network.network.id

    master {
        version = "1.24"
        zonal {
            zone      = "ru-central1-d"
            subnet_id = yandex_vpc_subnet.subnet.id
        }
        public_ip = true
        security_group_ids = [yandex_vpc_security_group.k8s.id]
    }

    service_account_id      = yandex_iam_service_account.k8s-sa.id
    node_service_account_id = yandex_iam_service_account.k8s-sa.id

    depends_on = [
        yandex_resourcemanager_folder_iam_binding.k8s-clusters-agent,
        yandex_resourcemanager_folder_iam_binding.vpc-public-admin,
        yandex_resourcemanager_folder_iam_binding.images-puller
    ]
}

resource "yandex_kubernetes_node_group" "node-group" {
    cluster_id = yandex_kubernetes_cluster.stock-exchange-k8s.id
    name       = "node-group"
    version    = "1.24"

    instance_template {
        platform_id = "standard-v2"

        resources {
            cores         = 2
            memory        = 4
        }

        boot_disk {
            type = "network-hdd"
            size = 64
        }

        network_interface {
            subnet_ids = [yandex_vpc_subnet.subnet.id]
            security_group_ids = [yandex_vpc_security_group.k8s.id]
            nat       = true
        }
    }

    scale_policy {
        fixed_scale {
            size = 1
        }
    }

    allocation_policy {
        location {
            zone = "ru-central1-d"
        }
    }
}