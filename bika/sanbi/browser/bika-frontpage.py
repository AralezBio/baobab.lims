from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone import api as ploneapi

from bika.lims.browser import BrowserView

class FrontPageView(BrowserView):
    template = ViewPageTemplateFile("bika-frontpage.pt")

    def __call__(self):
        self.set_versions()
        self.icon = self.portal_url + \
                    "/++resource++bika.lims.images/chevron_big.png"

        bika_setup = ploneapi.portal.get_tool("bika_setup")
        landingpage = bika_setup.getLandingPage()
        if self.is_anonymous_user():
            # Redirect to the selected Landing Page
            if landingpage:
                return self.request.response.redirect(landingpage.absolute_url())
            # Show the Bika Front Page
            return self.template()

        # Authenticated Users get either the Dashboard, the std. Bika Frontpage
        # or the custom landing page. Furthermore, they can switch between the
        # Dashboard and the landing page.

        # First precedence: Request parameter `redirect_to`
        redirect_to = self.request.form.get("redirect_to", None)
        if redirect_to == "dashboard":
            return self.request.response.redirect(self.portal_url + "/bika-dashboard")
        if redirect_to == "frontpage":
            if landingpage:
                return self.request.response.redirect(landingpage.absolute_url())
            return self.template()

        # Second precedence: Dashboard enabled
        if self.is_dashboard_enabled():
            roles = self.get_user_roles()
            if 'Manager' in roles or 'LabManager' in roles:
                return self.request.response.redirect(self.portal_url + "/bika-dashboard")
            if 'Sampler' in roles or 'SampleCoordinator' in roles:
                return self.request.response.redirect(
                    self.portal_url + "/samples?samples_review_state=to_be_sampled")

        # Third precedence: Custom Landing Page
        if landingpage:
            return self.request.response.redirect(landingpage.absolute_url())

        return self.template()

    def set_versions(self):
        """Configure a list of product versions from portal.quickinstaller
        """
        self.versions = {}
        self.upgrades = {}
        qi = self.context.portal_quickinstaller
        for key in qi.keys():
            info = qi.upgradeInfo('bika.sanbi')
            self.versions[key] = qi.getProductVersion(key)
            info = qi.upgradeInfo(key)
            if info and 'installedVersion' in info:
                self.upgrades[key] = info['installedVersion']

    def is_dashboard_enabled(self):
        """Checks if the dashboard is enabled
        """
        bika_setup = ploneapi.portal.get_tool("bika_setup")
        return bika_setup.getDashboardByDefault()

    def is_anonymous_user(self):
        """Checks if the current user is anonymous
        """
        return ploneapi.user.is_anonymous()

    def get_user_roles(self):
        """Returns a list of roles for the current user
        """
        if self.is_anonymous_user():
            return []
        current_user = ploneapi.user.get_current()
        return ploneapi.user.get_roles(user=current_user)

    def set_versions(self):
        """Configure a list of product versions from portal.quickinstaller
        """
        self.versions = {}
        self.upgrades = {}
        qi = ploneapi.portal.get_tool("portal_quickinstaller")
        for key in qi.keys():
            info = qi.upgradeInfo('bika.lims')
            self.versions[key] = qi.getProductVersion(key)
            info = qi.upgradeInfo(key)
            if info and 'installedVersion' in info:
                self.upgrades[key] = info['installedVersion']