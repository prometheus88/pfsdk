#!/bin/bash
# Setup GitHub branch protection rules
# Requires GitHub CLI (gh) to be installed and authenticated

set -e

REPO="allendy/pfsdk"

echo "🔒 Setting up branch protection for PostFiat SDK..."

# Protect main branch
echo "🛡️  Protecting main branch..."
gh api repos/$REPO/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Proto Validation","Code Generation","Code Quality","Tests","Security Scan","Build Package"]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true,"require_code_owner_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false

# Protect dev branch
echo "🛡️  Protecting dev branch..."
gh api repos/$REPO/branches/dev/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":["Proto Validation","Code Generation","Code Quality","Tests","Security Scan"]}' \
  --field enforce_admins=false \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false

echo "✅ Branch protection rules configured!"
echo ""
echo "📋 Summary:"
echo "  • main: Requires 1 approval, all CI checks, admin enforcement"
echo "  • develop: Requires 1 approval, all CI checks except build"
echo "  • Force pushes disabled on both branches"
echo "  • Branch deletions disabled on both branches"
echo ""
echo "🚀 Next steps:"
echo "  1. Create 'develop' branch: git checkout -b develop && git push -u origin develop"
echo "  2. Set develop as default branch in GitHub settings"
echo "  3. Configure PyPI trusted publishing for releases"
