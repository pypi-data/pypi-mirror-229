from .db import *
from .countries import get_country_iso2


class CiscoAPLookup:

    @classmethod
    def models(cls) -> list[str]:
        return get_models()

    @classmethod
    def domain_for(cls, model: str, cn_iso2: str = None) -> list[str]:
        """
        Get list of possible regulatory domains for AP model and optionally country
        :param str model: AP Model name (without regulatory domain part)
        :param str cn_iso2: iso2 country - detects iso2 from full name, but with perf. impact.
        :rtype: list[str]
        """
        if cn_iso2 and len(cn_iso2) > 2:
            cn_iso2 = get_country_iso2(cn_iso2)
        return get_domain_for(model, cn_iso2)

    @classmethod
    def models_for(cls, model: str, cn_iso2: str = None) -> list[str]:
        """
        Get list of AP model PIDs with RD for model and optionally country
        :param str model: AP Model name (without regulatory domain part)
        :param str cn_iso2: iso2 country - detects iso2 from full name, but with perf. impact.
        :rtype: list[str]
        """
        if cn_iso2 and len(cn_iso2) > 2:
            cn_iso2 = get_country_iso2(cn_iso2)
        return get_models_for(model, cn_iso2)

    @classmethod
    def country_models(cls, model: str) -> list[str]:
        """
        Get list of unique AP model PIDs with RD for model
        :param str model: AP Model name (without regulatory domain part)
        :rtype: list[str]
        """
        return get_models_for(model)


__all__ = ["CiscoAPLookup"]
