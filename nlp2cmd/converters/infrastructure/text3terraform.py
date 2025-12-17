"""
Text3Terraform - Generowanie konfiguracji Terraform.

Automatyczne generowanie Infrastructure as Code.
"""

from typing import Dict, Any, Optional, List
from nlp2cmd.core.base import BaseConverter, ConversionResult
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class Text3Terraform(BaseConverter):
    """
    Generator konfiguracji Terraform.
    
    Obsługuje:
    - AWS, GCP, Azure
    - Kubernetes clusters
    - Networks, VPCs
    - Storage, Databases
    - Load Balancers
    """
    
    # Templates for different providers
    PROVIDER_TEMPLATES = {
        "aws": '''terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}
''',
        "gcp": '''terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}
''',
        "azure": '''terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

variable "location" {
  description = "Azure location"
  type        = string
  default     = "East US"
}
'''
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def parse_intent(self, text: str) -> Dict[str, Any]:
        """
        Parsuje intencję z tekstu.
        
        Returns:
            {
                "provider": str,      # aws, gcp, azure
                "resource_type": str, # k8s, vpc, database, etc.
                "resources": List[str]
            }
        """
        text = text.strip().lower()
        
        # Detect provider
        provider = "aws"
        if "gcp" in text or "google cloud" in text:
            provider = "gcp"
        elif "azure" in text:
            provider = "azure"
        
        # Detect resource type
        resource_type = "general"
        if "kubernetes" in text or "k8s" in text or "eks" in text or "gke" in text:
            resource_type = "kubernetes"
        elif "vpc" in text or "network" in text:
            resource_type = "network"
        elif "database" in text or "rds" in text or "sql" in text:
            resource_type = "database"
        elif "storage" in text or "s3" in text or "bucket" in text:
            resource_type = "storage"
        elif "load balancer" in text or "alb" in text or "nlb" in text:
            resource_type = "loadbalancer"
        
        return {
            "provider": provider,
            "resource_type": resource_type,
            "description": text
        }
    
    def generate_command(self, intent: Dict[str, Any]) -> str:
        """Generuje konfigurację Terraform"""
        
        provider = intent["provider"]
        resource_type = intent["resource_type"]
        
        # Provider config
        config = self.PROVIDER_TEMPLATES.get(provider, self.PROVIDER_TEMPLATES["aws"])
        
        # Add resource-specific config
        if resource_type == "kubernetes":
            config += "\n" + self._generate_kubernetes_cluster(provider)
        elif resource_type == "network":
            config += "\n" + self._generate_vpc(provider)
        elif resource_type == "database":
            config += "\n" + self._generate_database(provider)
        elif resource_type == "storage":
            config += "\n" + self._generate_storage(provider)
        elif resource_type == "loadbalancer":
            config += "\n" + self._generate_loadbalancer(provider)
        else:
            config += "\n" + self._generate_general(provider)
        
        return config
    
    def _generate_kubernetes_cluster(self, provider: str) -> str:
        """Generuje Kubernetes cluster"""
        
        if provider == "aws":
            return '''
# EKS Cluster
resource "aws_eks_cluster" "main" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_cluster.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids = aws_subnet.private[*].id
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

# EKS Node Group
resource "aws_eks_node_group" "main" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "${var.cluster_name}-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = var.desired_nodes
    max_size     = var.max_nodes
    min_size     = var.min_nodes
  }

  instance_types = [var.instance_type]

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy
  ]
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "my-cluster"
}

variable "kubernetes_version" {
  description = "Kubernetes version"
  type        = string
  default     = "1.28"
}

variable "desired_nodes" {
  description = "Desired number of nodes"
  type        = number
  default     = 3
}

variable "max_nodes" {
  description = "Maximum number of nodes"
  type        = number
  default     = 5
}

variable "min_nodes" {
  description = "Minimum number of nodes"
  type        = number
  default     = 1
}

variable "instance_type" {
  description = "EC2 instance type for nodes"
  type        = string
  default     = "t3.medium"
}
'''
        elif provider == "gcp":
            return '''
# GKE Cluster
resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = var.region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name
}

# GKE Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.cluster_name}-node-pool"
  location   = var.region
  cluster    = google_container_cluster.primary.name
  node_count = var.desired_nodes

  node_config {
    machine_type = var.machine_type
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }

  autoscaling {
    min_node_count = var.min_nodes
    max_node_count = var.max_nodes
  }
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  default     = "my-cluster"
}

variable "machine_type" {
  description = "Machine type for nodes"
  type        = string
  default     = "e2-medium"
}

variable "desired_nodes" {
  description = "Number of nodes per zone"
  type        = number
  default     = 1
}

variable "max_nodes" {
  description = "Max nodes per zone"
  type        = number
  default     = 3
}

variable "min_nodes" {
  description = "Min nodes per zone"
  type        = number
  default     = 1
}
'''
        
        return "# Kubernetes cluster configuration"
    
    def _generate_vpc(self, provider: str) -> str:
        """Generuje VPC/Network"""
        
        if provider == "aws":
            return '''
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = var.vpc_name
  }
}

# Internet Gateway
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name = "${var.vpc_name}-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.vpc_name}-public-${count.index + 1}"
  }
}

# Private Subnets
resource "aws_subnet" "private" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, count.index + length(var.availability_zones))
  availability_zone = var.availability_zones[count.index]

  tags = {
    Name = "${var.vpc_name}-private-${count.index + 1}"
  }
}

variable "vpc_name" {
  description = "VPC name"
  type        = string
  default     = "main-vpc"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}
'''
        
        return "# Network configuration"
    
    def _generate_database(self, provider: str) -> str:
        """Generuje Database"""
        
        if provider == "aws":
            return '''
# RDS Database
resource "aws_db_instance" "main" {
  identifier        = var.db_name
  engine            = var.db_engine
  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_class
  allocated_storage = var.db_allocated_storage

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  backup_retention_period = 7
  skip_final_snapshot     = var.skip_final_snapshot

  tags = {
    Name = var.db_name
  }
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.db_name}-subnet-group"
  subnet_ids = aws_subnet.private[*].id

  tags = {
    Name = "${var.db_name}-subnet-group"
  }
}

# Security Group
resource "aws_security_group" "db" {
  name        = "${var.db_name}-sg"
  description = "Security group for database"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "mydb"
}

variable "db_engine" {
  description = "Database engine"
  type        = string
  default     = "postgres"
}

variable "db_engine_version" {
  description = "Database engine version"
  type        = string
  default     = "15.3"
}

variable "db_instance_class" {
  description = "Database instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage (GB)"
  type        = number
  default     = 20
}

variable "db_username" {
  description = "Database username"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

variable "skip_final_snapshot" {
  description = "Skip final snapshot on delete"
  type        = bool
  default     = false
}
'''
        
        return "# Database configuration"
    
    def _generate_storage(self, provider: str) -> str:
        """Generuje Storage"""
        
        if provider == "aws":
            return '''
# S3 Bucket
resource "aws_s3_bucket" "main" {
  bucket = var.bucket_name

  tags = {
    Name = var.bucket_name
  }
}

# Bucket versioning
resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Bucket encryption
resource "aws_s3_bucket_server_side_encryption_configuration" "main" {
  bucket = aws_s3_bucket.main.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Block public access
resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

variable "bucket_name" {
  description = "S3 bucket name"
  type        = string
}
'''
        
        return "# Storage configuration"
    
    def _generate_loadbalancer(self, provider: str) -> str:
        """Generuje Load Balancer"""
        
        return '''
# Application Load Balancer
resource "aws_lb" "main" {
  name               = var.lb_name
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false

  tags = {
    Name = var.lb_name
  }
}

# Target Group
resource "aws_lb_target_group" "main" {
  name     = "${var.lb_name}-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/health"
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
  }
}

# Listener
resource "aws_lb_listener" "main" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

variable "lb_name" {
  description = "Load balancer name"
  type        = string
  default     = "main-lb"
}
'''
    
    def _generate_general(self, provider: str) -> str:
        """Generuje ogólną konfigurację"""
        return "# Additional resources can be added here"
    
    def execute(self, text: str) -> ConversionResult:
        """
        Generuje konfigurację Terraform.
        
        Args:
            text: Opis infrastruktury w języku naturalnym
            
        Returns:
            Wynik z wygenerowaną konfiguracją
        """
        try:
            intent = self.parse_intent(text)
            config = self.generate_command(intent)
            
            return ConversionResult(
                success=True,
                command=f"Generated Terraform config for {intent['provider']}",
                output=config,
                metadata={
                    "provider": intent["provider"],
                    "resource_type": intent["resource_type"]
                }
            )
            
        except Exception as e:
            logger.error(f"Błąd generowania: {e}")
            return ConversionResult(
                success=False,
                error=str(e),
                metadata={"input": text}
            )
    
    def save_terraform(
        self,
        config: str,
        directory: str = "terraform"
    ) -> bool:
        """
        Zapisuje konfigurację Terraform do plików.
        
        Args:
            config: Konfiguracja Terraform
            directory: Katalog docelowy
            
        Returns:
            True jeśli sukces
        """
        try:
            path = Path(directory)
            path.mkdir(parents=True, exist_ok=True)
            
            # Save main config
            main_file = path / "main.tf"
            main_file.write_text(config)
            
            # Generate outputs.tf
            outputs_file = path / "outputs.tf"
            outputs_file.write_text(self._generate_outputs())
            
            # Generate terraform.tfvars.example
            tfvars_file = path / "terraform.tfvars.example"
            tfvars_file.write_text(self._generate_tfvars())
            
            logger.info(f"Zapisano konfigurację Terraform w: {directory}")
            return True
            
        except Exception as e:
            logger.error(f"Błąd zapisu: {e}")
            return False
    
    def _generate_outputs(self) -> str:
        """Generuje outputs.tf"""
        return '''# Outputs
output "cluster_endpoint" {
  description = "Cluster endpoint"
  value       = try(aws_eks_cluster.main.endpoint, "N/A")
}

output "vpc_id" {
  description = "VPC ID"
  value       = try(aws_vpc.main.id, "N/A")
}
'''
    
    def _generate_tfvars(self) -> str:
        """Generuje terraform.tfvars.example"""
        return '''# Example terraform.tfvars
# Copy this file to terraform.tfvars and fill in the values

region = "us-east-1"
# cluster_name = "my-cluster"
# vpc_cidr = "10.0.0.0/16"
'''
