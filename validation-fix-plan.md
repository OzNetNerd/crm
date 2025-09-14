# Fix Validation Errors in Simplified Route System

## Objective
Fix validation failures and WTForms errors in the new simplified route system that replaced the over-engineered universal builders.

## Key Changes
- [ ] Fix entity_buttons format in route contexts (should be dict with title/url, not string array)
- [ ] Add missing `multiple` and `searchable` fields to dropdown_configs in all routes
- [ ] Create safe integer coercion for WTForms SelectField `coerce=int` issues
- [ ] Update stakeholders route dropdown configs to pass validation
- [ ] Apply same fixes to all other entity routes (opportunities, teams, etc.)

## Files to Modify/Create
- `app/utils/forms/helpers.py` - Create safe_int_coerce function (new file)
- `app/forms/entities/stakeholder.py` - Replace coerce=int with safe version
- `app/forms/entities/opportunity.py` - Replace coerce=int with safe version
- `app/routes/web/stakeholders.py` - Fix entity_buttons and add missing dropdown fields
- `app/routes/web/opportunities.py` - Fix entity_buttons and add missing dropdown fields
- `app/routes/web/teams.py` - Fix entity_buttons and add missing dropdown fields
- `app/routes/web/companies.py` - Fix entity_buttons and add missing dropdown fields

## Implementation Order
1. Create safe integer coercion helper for forms (prevents WTForms crashes)
2. Fix entity_buttons structure from string array to proper dict format
3. Add missing `multiple: False, searchable: True` to all dropdown configs
4. Replace coerce=int in stakeholder and opportunity forms
5. Test all entity routes to ensure validation passes

## Risks & Considerations
- Must work with the simplified route system, not universal builders
- Entity buttons structure change may require template updates
- Each route needs individual fixes since no universal system exists
- Safe coercion must handle None, empty string, and invalid integer cases