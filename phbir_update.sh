git pull
bench --site erpnextsandbox.serviotech.com migrate
bench --site erpnextsandbox.serviotech.com clear-cache
bench --site erpnextsandbox.serviotech.com clear-website-cache
sudo supervisorctl restart frappe-bench-sandbox-workers:*
sudo supervisorctl restart frappe-bench-sandbox-web:*
sudo supervisorctl restart frappe-bench-sandbox-redis:*