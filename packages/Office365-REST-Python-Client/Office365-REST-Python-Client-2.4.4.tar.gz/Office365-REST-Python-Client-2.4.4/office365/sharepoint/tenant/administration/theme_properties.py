from office365.sharepoint.base_entity import BaseEntity


class ThemeProperties(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.Online.SharePoint.TenantManagement.ThemeProperties"
