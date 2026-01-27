# Justfile for managing the freqtrade-testing Helm chart

# Default variables
default_release_name := "freqtrade-testing"
default_namespace := "freqtrade-testing"
values_arg := `if [ -f custom-values.yaml ]; then echo "-f custom-values.yaml"; fi`

# Alias for help
default:
    @just --list

# --- Chart Management ---

# Lint the Helm chart
lint:
    @echo "Linting Helm chart..."
    helm lint . {{values_arg}}

# Template the Helm chart
template release_name=default_release_name namespace=default_namespace:
    @echo "Templating Helm chart..."
    helm template {{release_name}} . -n {{namespace}} {{values_arg}}

# --- Installation and Uninstallation ---

# Install the Helm chart
install release_name=default_release_name namespace=default_namespace:
    @echo "Installing Helm chart..."
    helm install {{release_name}} . -n {{namespace}} --create-namespace {{values_arg}}

# Upgrade the Helm chart
upgrade release_name=default_release_name namespace=default_namespace:
    @echo "Upgrading Helm chart..."
    helm upgrade {{release_name}} . -n {{namespace}} {{values_arg}}

# Uninstall the Helm chart
uninstall release_name=default_release_name namespace=default_namespace:
    @echo "Uninstalling Helm chart..."
    helm uninstall {{release_name}} -n {{namespace}}

# --- Logs ---

# Stream logs from testing container
logs-testing namespace=default_namespace:
    kubectl -n {{namespace}} logs -f {{default_release_name}}-{{default_release_name}}-0 -c testing

# Stream logs from ui container
logs-ui namespace=default_namespace:
    kubectl -n {{namespace}} logs -f {{default_release_name}}-{{default_release_name}}-0 -c ui

# --- Namespace ---

# Create the namespace
create-ns namespace=default_namespace:
    @echo "Creating namespace: {{namespace}}"
    kubectl create namespace {{namespace}}

# Delete the namespace
delete-ns namespace=default_namespace:
    @echo "Deleting namespace: {{namespace}}"
    kubectl delete namespace {{namespace}}
