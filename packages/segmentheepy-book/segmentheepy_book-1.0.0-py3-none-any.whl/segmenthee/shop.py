from segmenthee.cart_api import *
from datetime import datetime as dt
import json
import re
from urllib.parse import urlparse, parse_qs, unquote


CATEGORY_MAP: Dict[str, int] = {
    'hu-book': 0,
    'hu-kids_normal': 1, 
    'hu-ebook': 2,
    'hu-audiobook_normal': 3,
    'hu-oldbook': 4,
    'hu-foreign': 5,
    'hu-music_normal': 6,
    'hu-film_normal': 7,
    'hu-other_normal': 8
}

CATEGORY_MAP_VIEW_ITEM: Dict[str, int] = {
    'book': 0,
    'kids': 1, 
    'ebook': 2,
    'audiobook': 3, 
    'oldbook': 4,
    'foreign': 5,
    'audio': 6,
    'film': 7,
    'other': 8
}

CATEGORY_FILTER: Dict[int, int] = {}

PREDEFINED_FILTER: Dict[str, int] = {}


INFO_PAGES: List[str] = [
    '/news/news.action',
    '/news/help.action',
    '/adatvedelmi-nyilatkozat-44',
    '/giftcard/giftCard!input.action',
    '/stp/viewProducts.action'
]


def get_event(item: Dict) -> SessionBodyEvent:
    if item.get('v') == '2':
        return get_event_ga4(item)

    return get_event_ua(item)


def get_event_ga4(item: Dict) -> SessionBodyEvent:
    hit_time: int = int(item.get('_ts', int(dt.now().timestamp())))
    kwargs: Dict[str, Any] = {
        'time': hit_time,
        'referrer': get_referrer(item.get('dr')),
        'tabcount': int(item.get('s_tc')),
        'tabtype': get_tabtype(item.get('s_tt')),
        'navigation': get_navigation(item.get('s_nt')),
        'redirects': int(item.get('s_rc')),
        'title': item.get('dt'),
        'utm_source': get_utm_source(item),
        'utm_medium': item.get('utm_medium', '')
    }
    event_name: str = item.get('en')

    if event_name == 'scroll':
        return ProductPageScrollEvent(**kwargs)

    if event_name == 'add_to_cart':
        delta_count: int = int(item.get('qty'))
        delta_total: int = round(float(item.get('val')))
        return CartModifyEvent(hit_time, delta_count, delta_total)

    if event_name == 'remove_from_cart':
        delta_count: int = -1 * int(item.get('qty'))
        delta_total: int = -1 * round(float(item.get('val')))
        return CartModifyEvent(hit_time, delta_count, delta_total)

    if event_name == 'coupon_offered':
        return CouponOfferedEvent(hit_time, item.get('el'))

    if event_name == 'coupon_accepted':
        return CouponAcceptedEvent(hit_time, item.get('el'))

    if event_name == 'coupon_rejected':
        return CouponRejectedEvent(hit_time, item.get('el'))

    if event_name == 'begin_checkout':
        return CustomerDataEntryBrowsingEvent(**kwargs)

    if event_name == 'add_shipping_info':
        return ShippingMethodBrowsingEvent(**kwargs)

    if event_name == 'add_payment_info':
        return PaymentMethodBrowsingEvent(**kwargs)

    if event_name == 'purchase':
        return CheckoutSuccessPageBrowsingEvent(**kwargs)   

    if event_name == 'view_cart':
        return CartBrowsingEvent(**kwargs)

    if event_name == 'view_wishlist':
        return WishListBrowsingEvent(**kwargs)

    if event_name == 'view_account_pages':
        return AccountPageBrowsingEvent(**kwargs)
    
    parts = urlparse(get_fixed_url(item.get('dl')))
    query: Dict[str, str] = parse_query(parts.query)

    if event_name == 'view_item':
        kwargs['product_id'] = item.get('pr1id')
        # segmenthee library needs to parse breadcrumb and sends first link href as pr1ca
        kwargs['category_id'] = -1
        query_id = item.get('pr1ca', '')
        for id_param, category in CATEGORY_MAP_VIEW_ITEM.items():
            if query_id == id_param:
                kwargs['category_id'] = category
                break

        kwargs['price'] = float_or_none(item.get('pr1pr'))
        return ProductPageBrowsingEvent(**kwargs)

    # CategoryPage dedicated
    if event_name == 'category_page':
        kwargs['category_id'] = -1
        query_id = item.get('category', '')
        for id_param, category in CATEGORY_MAP_VIEW_ITEM.items():
            if query_id == id_param:
                kwargs['category_id'] = category
                break

        kwargs = {**kwargs, **get_pagination(query)}
        return CategoryPageBrowsingEvent(**kwargs)

    if parts.path == '/':
        return MainPageBrowsingEvent(**kwargs)

    if parts.path == '/szakuzletunk':
        return ShopListBrowsingEvent(**kwargs)

    if parts.path == '/reflexshop-tarsasjatekok':
        return BoardGamesUpdateEvent(**kwargs)

    if parts.path == '/index.php' and query.get('route') == 'wishlist/wishlist':
        return WishListBrowsingEvent(**kwargs)

    if parts.path == '/index.php' and query.get('route', '').startswith('account/'):
        return AccountPageBrowsingEvent(**kwargs)

    # CategoryPage
    if parts.path == '/search/categories.action':
        query_id = query.get('id')
        for id_param, category in CATEGORY_MAP.items():
            if query_id.find(id_param) > -1:
                kwargs = {**kwargs, 'category_id': category, **get_pagination(query)}
                return CategoryPageBrowsingEvent(**kwargs)

    # CategoryPage
    if parts.path == '/index.php' and query.get('route') == 'product/list':
        if query.get('keyword') is None and (cat_id := query.get('category_id')):
            category = CATEGORY_FILTER.get(int(cat_id), -1)
            kwargs = {**kwargs, 'category_id': category, **get_pagination(query)}
            return CategoryPageBrowsingEvent(**kwargs)

    # PredefinedFilter -> CategoryPage -> SearchResults
    if parts.path == '/index.php' and query.get('route') == 'filter':
        category = PREDEFINED_FILTER.get(query.get('filter'), -2)
        if category > -2:
            kwargs = {**kwargs, 'category_id': category, **get_pagination(query)}
            return PredefinedFilterBrowsingEvent(**kwargs)

        if query.get('filter', '').startswith('category|') and query.get('keyword') is None:
            numbers = re.findall(r'\d+', query.get('filter'))
            category = CATEGORY_FILTER.get(int(numbers[0]), -2) if numbers else -2
            if category > -2:
                kwargs = {**kwargs, 'category_id': category, **get_pagination(query)}
                return CategoryPageBrowsingEvent(**kwargs)

        kwargs = {**kwargs, **get_pagination(query)}
        return SearchResultsBrowsingEvent(**kwargs)

    # SearchResults
    if event_name == 'search':
        kwargs = {**kwargs, **get_pagination(query)}
        return SearchResultsBrowsingEvent(**kwargs)

    # InformationPage
    if parts.path in INFO_PAGES or query.get('route') in INFO_PAGES:
        return InformationPageBrowsingEvent(**kwargs)

    return BrowsingEvent(**kwargs)


def float_or_none(value: str):
    try:
        return float(value)
    except:
        return None


def get_event_ua(item: Dict) -> SessionBodyEvent:
    time: int = item.get('_ts', int(dt.now().timestamp()))
    browsing_data = {'time': time,
                     'referrer': get_referrer(item.get(Config.CD_REFERRER)),
                     'tabcount': int(item[Config.CD_TABCOUNT]),
                     'tabtype': get_tabtype(item[Config.CD_TABTYPE]),
                     'navigation': get_navigation(item[Config.CD_NAVIGATION]),
                     'redirects': int(item[Config.CD_REDIRECTS]),
                     'title': item.get('dt'),
                     'utm_source': get_utm_source(item),
                     'utm_medium': item.get('utm_medium', '')}

    if item.get('t') == 'pageview':
        parts = urlparse(get_fixed_url(item.get('dl')))
        query: Dict[str, str] = parse_query(parts.query)
        if parts.path == '/':
            event = MainPageBrowsingEvent(**browsing_data)
            return event
        if item.get('pa') == 'detail':
            browsing_data['product_id'] = item.get('pr1id')
            browsing_data['category_id'] = -1
            for path, cat in CATEGORY_MAP.items():
                if parts.path.startswith(path):
                    browsing_data['category_id'] = cat
                    break

            pr1pr = item.get('pr1pr', 0)
            browsing_data['price'] = int(pr1pr) if pr1pr != 'NaN' else 0
            event = ProductPageBrowsingEvent(**browsing_data)
            return event
        if parts.path == '/szakuzletunk':
            event = ShopListBrowsingEvent(**browsing_data)
            return event
        if parts.path == '/reflexshop-tarsasjatekok':
            event = BoardGamesUpdateEvent(**browsing_data)
            return event
        if parts.path == '/cart':
            event = CartBrowsingEvent(**browsing_data)
            return event
        if parts.path == '/checkout':
            if parts.fragment == '/customerdata/':
                event = CustomerDataEntryBrowsingEvent(**browsing_data)
                return event
            if parts.fragment == '/shippingmethod/':
                event = ShippingMethodBrowsingEvent(**browsing_data)
                return event
            if parts.fragment == '/paymentmethod/':
                event = PaymentMethodBrowsingEvent(**browsing_data)
                return event
            if parts.fragment == '/confirmation/':
                event = ConfirmationPageBrowsingEvent(**browsing_data)
                return event

            event = CheckoutPageBrowsingEvent(**browsing_data)
            return event

        if parts.path == '/index.php' and query.get('route') == 'checkout/success':
            event = CheckoutSuccessPageBrowsingEvent(**browsing_data)
            return event

        if parts.path == '/index.php' and query.get('route') == 'wishlist/wishlist':
            event = WishListBrowsingEvent(**browsing_data)
            return event

        if parts.path == '/index.php' and query.get('route', '').startswith('account/'):
            event = AccountPageBrowsingEvent(**browsing_data)
            return event

        # CategoryPage
        for path, category in CATEGORY_MAP.items():
            if parts.path == path or parts.path.find(path) > -1:
                kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                event = CategoryPageBrowsingEvent(**kwargs)
                return event

        # CategoryPage
        if parts.path == '/index.php' and query.get('route') == 'product/list':
            if query.get('keyword') is None and (cat_id := query.get('category_id')):
                category = CATEGORY_FILTER.get(int(cat_id), -1)
                kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                event = CategoryPageBrowsingEvent(**kwargs)
                return event

        # PredefinedFilter -> CategoryPage -> SearchResults
        if parts.path == '/index.php' and query.get('route') == 'filter':
            category = PREDEFINED_FILTER.get(query.get('filter'), -2)
            if category > -2:
                kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                event = PredefinedFilterBrowsingEvent(**kwargs)
                return event

            if query.get('filter', '').startswith('category|') and query.get('keyword') is None:
                numbers = re.findall(r'\d+', query.get('filter'))
                category = CATEGORY_FILTER.get(int(numbers[0]), -2) if numbers else -2
                if category > -2:
                    kwargs = {**browsing_data, 'category_id': category, **get_pagination(query)}
                    event = CategoryPageBrowsingEvent(**kwargs)
                    return event

            kwargs = {**browsing_data, **get_pagination(query)}
            event = SearchResultsBrowsingEvent(**kwargs)
            return event

        # SearchResults
        if parts.path == '/kereses' or query.get('route') == 'product/list':
            kwargs = {**browsing_data, **get_pagination(query)}
            event = SearchResultsBrowsingEvent(**kwargs)
            return event

        # InformationPage
        if parts.path in INFO_PAGES or query.get('route') in INFO_PAGES:
            event = InformationPageBrowsingEvent(**browsing_data)
            return event

        event = BrowsingEvent(**browsing_data)
        return event

    if item.get('t') == 'event':
        if item.get('ec') == 'Értesítés kérése' and item.get('ea') == 'Értesítés kérése sikeres':
            event = RegistrationEvent(time)
            return event
        if item.get('ec') == 'e-cart' and item.get('ea') == 'update':
            data = json.loads(item.get('el'))
            delta_count = data.get('itemCount')
            delta_total = round(data.get('total'), 2)
            event = CartModifyEvent(time, delta_count, delta_total)
            return event
        if item.get('ec') == 'OptiMonk':
            if item.get('ea') == 'shown':
                event = CouponOfferedEvent(time, item.get('el'))
                return event
            if item.get('ea') == 'filled':
                event = CouponAcceptedEvent(time, item.get('el'))
                return event

    event = SystemEvent(time)
    return event


def get_fixed_url(url: str) -> str:
    p1 = url.find('?')
    p2 = url.find('&')
    if p1 == -1 and p2 > -1:
        return url[:p2] + '?' + url[p2+1:]
    return url[:p2] + url[p1:] + url[p2:p1] if -1 < p2 < p1 else url


def parse_query(query: str) -> Dict[str, str]:
    return {} if query.strip() == '' else {k: v[0] for k, v in parse_qs(unquote(query)).items()}


def get_pagination(query: Dict) -> Dict:
    pagination = {"page": get_page(query.get('page', '1'))}
    if 'sortBy' in query.keys():
        pagination["sort"] = get_sort(query.get('sortBy'))
    else:
        pagination["sort"] = get_sort('default')
    return pagination
