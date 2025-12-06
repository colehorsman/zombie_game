"""AWS IAM Client for fetching permission data.

This module provides permission lookup for zombie identities, showing
what policies they had attached. Currently uses placeholder data but
can be extended to use real AWS IAM API calls.

**Feature: story-mode-education**
**Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7**
"""

import logging
import random
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

# High-risk AWS managed policies that grant broad permissions
HIGH_RISK_POLICIES = [
    "AdministratorAccess",
    "IAMFullAccess",
    "PowerUserAccess",
    "AmazonS3FullAccess",
    "AmazonEC2FullAccess",
    "AmazonRDSFullAccess",
    "SecretsManagerReadWrite",
    "AWSLambda_FullAccess",
]

# Common AWS managed policies for placeholder data
COMMON_POLICIES = [
    "AmazonS3ReadOnlyAccess",
    "AmazonEC2ReadOnlyAccess",
    "CloudWatchLogsReadOnlyAccess",
    "AmazonDynamoDBReadOnlyAccess",
    "AWSLambdaBasicExecutionRole",
    "AmazonSQSReadOnlyAccess",
    "AmazonSNSReadOnlyAccess",
    "ViewOnlyAccess",
]


@dataclass
class PermissionSummary:
    """Summary of permissions for an IAM identity.

    **Feature: story-mode-education**
    **Requirements: 6.3, 6.5**
    """

    attached_policies: List[str] = field(default_factory=list)
    inline_policies: List[str] = field(default_factory=list)
    high_risk_policies: List[str] = field(default_factory=list)
    trust_policy: Optional[str] = None  # For Roles only
    fetch_error: Optional[str] = None  # Error message if fetch failed

    @property
    def has_high_risk(self) -> bool:
        """Check if any high-risk policies are attached."""
        return len(self.high_risk_policies) > 0

    @property
    def total_policies(self) -> int:
        """Total number of policies attached."""
        return len(self.attached_policies) + len(self.inline_policies)

    def get_display_summary(self, max_policies: int = 3) -> str:
        """
        Get a formatted summary for display in dialogue.

        Args:
            max_policies: Maximum number of policies to show

        Returns:
            Formatted string for display
        """
        if self.fetch_error:
            return f"⚠️ Permissions unavailable: {self.fetch_error}"

        lines = []

        # Show high-risk policies first (in red conceptually)
        if self.high_risk_policies:
            lines.append("🔴 HIGH-RISK POLICIES:")
            for policy in self.high_risk_policies[:max_policies]:
                lines.append(f"  • {policy}")
            if len(self.high_risk_policies) > max_policies:
                lines.append(f"  ... and {len(self.high_risk_policies) - max_policies} more")

        # Show other attached policies
        other_policies = [p for p in self.attached_policies if p not in self.high_risk_policies]
        if other_policies:
            lines.append("📋 Attached Policies:")
            for policy in other_policies[:max_policies]:
                lines.append(f"  • {policy}")
            if len(other_policies) > max_policies:
                lines.append(f"  ... and {len(other_policies) - max_policies} more")

        # Show inline policies count
        if self.inline_policies:
            lines.append(f"📝 Inline Policies: {len(self.inline_policies)}")

        if not lines:
            lines.append("No policies attached")

        return "\n".join(lines)


class AWSIAMClient:
    """Client for fetching IAM permission data.

    Currently uses placeholder data. To use real AWS IAM API:
    1. Install boto3: pip install boto3
    2. Configure AWS credentials
    3. Replace _generate_placeholder_* methods with real API calls

    **Feature: story-mode-education**
    **Requirements: 6.1, 6.2, 6.6, 6.7**
    """

    def __init__(self, use_placeholder: bool = True):
        """
        Initialize the IAM client.

        Args:
            use_placeholder: If True, use placeholder data instead of real API
        """
        self.use_placeholder = use_placeholder
        self._cache: dict = {}  # Cache permission lookups
        logger.info(f"AWSIAMClient initialized (placeholder={use_placeholder})")

    @staticmethod
    def srn_to_arn(srn: str) -> Optional[str]:
        """
        Convert Sonrai SRN to AWS ARN format.

        SRN format: srn:aws:iam::ACCOUNT:TYPE/NAME
        ARN format: arn:aws:iam::ACCOUNT:TYPE/NAME

        Args:
            srn: Sonrai Resource Name

        Returns:
            AWS ARN or None if conversion fails

        **Feature: story-mode-education, Property 8: SRN to ARN Conversion**
        **Validates: Requirements 6.1**
        """
        if not srn:
            return None

        try:
            # Handle various SRN formats
            if srn.startswith("srn:"):
                # Direct conversion: srn: -> arn:
                return srn.replace("srn:", "arn:", 1)
            elif srn.startswith("arn:"):
                # Already an ARN
                return srn
            else:
                # Try to construct ARN from identity info
                # Format: account/type/name or similar
                logger.warning(f"Unknown SRN format: {srn}")
                return None
        except Exception as e:
            logger.error(f"Failed to convert SRN to ARN: {e}")
            return None

    def get_user_policies(self, user_name: str, account: str = None) -> PermissionSummary:
        """
        Fetch policies attached to an IAM User.

        Args:
            user_name: Name of the IAM user
            account: AWS account ID (for caching)

        Returns:
            PermissionSummary with attached policies

        **Feature: story-mode-education**
        **Requirements: 6.2**
        """
        cache_key = f"user:{account}:{user_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.use_placeholder:
            summary = self._generate_placeholder_user_permissions(user_name)
        else:
            summary = self._fetch_real_user_permissions(user_name)

        self._cache[cache_key] = summary
        return summary

    def get_role_policies(self, role_name: str, account: str = None) -> PermissionSummary:
        """
        Fetch policies attached to an IAM Role.

        Args:
            role_name: Name of the IAM role
            account: AWS account ID (for caching)

        Returns:
            PermissionSummary with attached policies and trust policy

        **Feature: story-mode-education**
        **Requirements: 6.2**
        """
        cache_key = f"role:{account}:{role_name}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if self.use_placeholder:
            summary = self._generate_placeholder_role_permissions(role_name)
        else:
            summary = self._fetch_real_role_permissions(role_name)

        self._cache[cache_key] = summary
        return summary

    def get_permissions(
        self, identity_name: str, identity_type: str, account: str = None
    ) -> PermissionSummary:
        """
        Fetch permissions for any identity type.

        Args:
            identity_name: Name of the identity
            identity_type: Type (User, Role, etc.)
            account: AWS account ID

        Returns:
            PermissionSummary
        """
        identity_type_lower = identity_type.lower()

        if "user" in identity_type_lower:
            return self.get_user_policies(identity_name, account)
        elif "role" in identity_type_lower:
            return self.get_role_policies(identity_name, account)
        else:
            # Unknown type - return empty with note
            return PermissionSummary(fetch_error=f"Unknown identity type: {identity_type}")

    def is_high_risk(self, policy_name: str) -> bool:
        """
        Check if a policy is considered high-risk.

        Args:
            policy_name: Name of the policy

        Returns:
            True if high-risk

        **Feature: story-mode-education, Property 10: High-Risk Policy Detection**
        **Validates: Requirements 6.4**
        """
        return policy_name in HIGH_RISK_POLICIES

    def clear_cache(self) -> None:
        """Clear the permission cache."""
        self._cache.clear()
        logger.info("Permission cache cleared")

    # ========== Placeholder Data Generation ==========

    def _generate_placeholder_user_permissions(self, user_name: str) -> PermissionSummary:
        """Generate realistic placeholder permissions for a User."""
        # Use user_name hash for consistent random data
        random.seed(hash(user_name) % 2**32)

        attached = []
        high_risk = []

        # 30% chance of having a high-risk policy
        if random.random() < 0.3:
            hr_policy = random.choice(HIGH_RISK_POLICIES)
            attached.append(hr_policy)
            high_risk.append(hr_policy)

        # Add 1-4 common policies
        num_policies = random.randint(1, 4)
        attached.extend(random.sample(COMMON_POLICIES, min(num_policies, len(COMMON_POLICIES))))

        # 20% chance of inline policies
        inline = []
        if random.random() < 0.2:
            inline = [f"{user_name}-custom-policy"]

        random.seed()  # Reset random state
        return PermissionSummary(
            attached_policies=attached,
            inline_policies=inline,
            high_risk_policies=high_risk,
        )

    def _generate_placeholder_role_permissions(self, role_name: str) -> PermissionSummary:
        """Generate realistic placeholder permissions for a Role."""
        # Use role_name hash for consistent random data
        random.seed(hash(role_name) % 2**32)

        attached = []
        high_risk = []

        # 50% chance of having a high-risk policy (roles often have more permissions)
        if random.random() < 0.5:
            hr_policy = random.choice(HIGH_RISK_POLICIES)
            attached.append(hr_policy)
            high_risk.append(hr_policy)

        # Add 2-5 common policies
        num_policies = random.randint(2, 5)
        attached.extend(random.sample(COMMON_POLICIES, min(num_policies, len(COMMON_POLICIES))))

        # 40% chance of inline policies
        inline = []
        if random.random() < 0.4:
            inline = [f"{role_name}-inline-policy"]

        # Generate trust policy summary
        trust_principals = random.choice(
            [
                "ec2.amazonaws.com",
                "lambda.amazonaws.com",
                "ecs-tasks.amazonaws.com",
                "Account: 123456789012",
            ]
        )

        random.seed()  # Reset random state
        return PermissionSummary(
            attached_policies=attached,
            inline_policies=inline,
            high_risk_policies=high_risk,
            trust_policy=f"Trusted by: {trust_principals}",
        )

    # ========== Real AWS API Methods (Stubs) ==========

    def _fetch_real_user_permissions(self, user_name: str) -> PermissionSummary:
        """
        Fetch real permissions from AWS IAM API.

        TODO: Implement with boto3:
        ```python
        import boto3
        iam = boto3.client('iam')

        # Get attached policies
        attached = iam.list_attached_user_policies(UserName=user_name)

        # Get inline policies
        inline = iam.list_user_policies(UserName=user_name)
        ```
        """
        return PermissionSummary(fetch_error="Real AWS API not configured - using placeholder data")

    def _fetch_real_role_permissions(self, role_name: str) -> PermissionSummary:
        """
        Fetch real permissions from AWS IAM API.

        TODO: Implement with boto3:
        ```python
        import boto3
        iam = boto3.client('iam')

        # Get attached policies
        attached = iam.list_attached_role_policies(RoleName=role_name)

        # Get inline policies
        inline = iam.list_role_policies(RoleName=role_name)

        # Get trust policy
        role = iam.get_role(RoleName=role_name)
        trust = role['Role']['AssumeRolePolicyDocument']
        ```
        """
        return PermissionSummary(fetch_error="Real AWS API not configured - using placeholder data")
