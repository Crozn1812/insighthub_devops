terraform {
  # Source contract only. The local-only track always initializes with
  # `terraform init -backend=false` and never accesses this non-live bucket.
  backend "s3" {
    bucket       = "insighthub-do2603-tfstate-localonly-disabled"
    key          = "day3/terraform.tfstate"
    region       = "ap-southeast-1"
    encrypt      = true
    use_lockfile = true
  }
}
