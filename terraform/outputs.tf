output "pg_host" {
    value = yandex_mdb_postgresql_cluster.stock-exchange-db.host[0].fqdn
}

output "k8s_cluster_id" {
    value = yandex_kubernetes_cluster.stock-exchange-k8s.id
}