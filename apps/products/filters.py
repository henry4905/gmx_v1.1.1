from django.db.models import Min, Max

from .models import (
    Category,
    Brand,
    Country,
    CategoryAttribute,
    ProductAttribute,
    ProductAttributeValue,
    ProductCustomAttributeValue,
)
from apps.accounts.models import (
    ImporterProfile,
    ImporterParameter,
    ImporterParameterValue,
)


# =========================================================
# Helpers
# =========================================================

def ensure_dict(value):
    return value if isinstance(value, dict) else {}


def to_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        val = value.strip().lower()

        if val in ["true", "1", "yes", "այո"]:
            return True

        if val in ["false", "0", "no", "ոչ"]:
            return False

    return value


def to_number(value):
    if value in [None, ""]:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def normalize_single_value(value):
    if isinstance(value, str):
        stripped = value.strip()

        bool_value = to_bool(stripped)
        if isinstance(bool_value, bool):
            return bool_value

        number_value = to_number(stripped)
        if number_value is not None:
            return number_value

        return stripped

    return value


def normalize_list_value(value):
    if not isinstance(value, list):
        value = [value]

    normalized = []

    for item in value:
        if item in [None, "", []]:
            continue
        normalized.append(normalize_single_value(item))

    return normalized


def normalize_range_value(value):
    if not isinstance(value, dict):
        return None

    min_value = normalize_single_value(value.get("min"))
    max_value = normalize_single_value(value.get("max"))

    if min_value is None and max_value is None:
        return None

    return {
        "min": min_value,
        "max": max_value,
    }


def get_selected_map(data, key):
    value = data.get(key, {})
    return value if isinstance(value, dict) else {}


def get_all_children(category):
    children = category.children.filter(is_active=True).order_by("name")
    all_children = list(children)

    for child in children:
        all_children.extend(get_all_children(child))

    return all_children


def get_category_ancestors_inclusive(category):
    chain = []

    current = category
    while current:
        chain.append(current)
        current = current.parent

    chain.reverse()
    return chain


def get_category_ancestor_ids(category_id):
    if not category_id:
        return []

    try:
        category = Category.objects.select_related("parent").get(
            id=category_id,
            is_active=True
        )
    except Category.DoesNotExist:
        return []

    return [item.id for item in get_category_ancestors_inclusive(category)]


def get_category_scope_queryset(base_queryset, category_id):
    if not category_id:
        return base_queryset
    return apply_category_filter(base_queryset, category_id)


# =========================================================
# Category
# =========================================================

def apply_category_filter(queryset, category_id):
    if not category_id:
        return queryset

    try:
        category = Category.objects.get(id=category_id, is_active=True)
    except Category.DoesNotExist:
        return queryset.none()

    children = get_all_children(category)
    category_ids = [category.id] + [child.id for child in children]

    return queryset.filter(category_id__in=category_ids)


# =========================================================
# Static filters
# =========================================================

def apply_static_filters(queryset, data, skip_keys=None):
    skip_keys = skip_keys or set()

    importer_id = data.get("importer")
    brand_id = data.get("brand")
    country_id = data.get("country_of_manufacture")
    status = data.get("status")
    price_min = to_number(data.get("price_min"))
    price_max = to_number(data.get("price_max"))

    if importer_id and "importer" not in skip_keys:
        queryset = queryset.filter(importer_id=importer_id)

    if brand_id and "brand" not in skip_keys:
        queryset = queryset.filter(brand_id=brand_id)

    if country_id and "country_of_manufacture" not in skip_keys:
        queryset = queryset.filter(country_of_manufacture_id=country_id)

    if status in ["available", "on_order"] and "status" not in skip_keys:
        queryset = queryset.filter(status=status)

    if price_min is not None and "price_min" not in skip_keys:
        queryset = queryset.filter(price_max__gte=price_min)

    if price_max is not None and "price_max" not in skip_keys:
        queryset = queryset.filter(price_min__lte=price_max)

    return queryset


# =========================================================
# Product category attributes
# data["attributes"] = {
#   "attr_id": ["A", "B"]
#   "attr_id": {"min": 10, "max": 100}
#   "attr_id": true
# }
# =========================================================

def apply_attribute_filters(queryset, data, skip_attr_id=None):
    attributes = ensure_dict(data.get("attributes", {}))

    if not attributes:
        return queryset

    for attr_id, raw_value in attributes.items():
        if str(attr_id) == str(skip_attr_id):
            continue

        if raw_value in [None, "", []]:
            continue

        value_qs = ProductAttributeValue.objects.filter(
            attribute_id=attr_id,
            attribute__is_main_filter=True
        )

        range_value = normalize_range_value(raw_value)
        if range_value:
            if range_value["min"] is not None:
                value_qs = value_qs.filter(value_number__gte=range_value["min"])

            if range_value["max"] is not None:
                value_qs = value_qs.filter(value_number__lte=range_value["max"])
        else:
            values = normalize_list_value(raw_value)
            if not values:
                continue

            text_values = [v for v in values if isinstance(v, str)]
            number_values = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            bool_values = [v for v in values if isinstance(v, bool)]

            matched_ids = set()

            if text_values:
                matched_ids.update(
                    value_qs.filter(value_text__in=text_values).values_list("product_id", flat=True)
                )

            if number_values:
                matched_ids.update(
                    value_qs.filter(value_number__in=number_values).values_list("product_id", flat=True)
                )

            if bool_values:
                matched_ids.update(
                    value_qs.filter(value_boolean__in=bool_values).values_list("product_id", flat=True)
                )

            queryset = queryset.filter(id__in=matched_ids).distinct()
            continue

        matched_ids = value_qs.values_list("product_id", flat=True).distinct()
        queryset = queryset.filter(id__in=matched_ids).distinct()

    return queryset.distinct()


# =========================================================
# Product custom attributes
# data["custom_attributes"] = {
#   "attr_id": ["A", "B"]
#   "attr_id": {"min": 10, "max": 100}
#   "attr_id": true
# }
# =========================================================

def apply_custom_attribute_filters(queryset, data, skip_custom_attr_id=None):
    custom_attributes = ensure_dict(data.get("custom_attributes", {}))

    if not custom_attributes:
        return queryset

    for attr_id, raw_value in custom_attributes.items():
        if str(attr_id) == str(skip_custom_attr_id):
            continue

        if raw_value in [None, "", []]:
            continue

        value_qs = ProductCustomAttributeValue.objects.filter(
            attribute_id=attr_id,
            attribute__is_main_filter=True
        )

        range_value = normalize_range_value(raw_value)
        if range_value:
            if range_value["min"] is not None:
                value_qs = value_qs.filter(value_number__gte=range_value["min"])

            if range_value["max"] is not None:
                value_qs = value_qs.filter(value_number__lte=range_value["max"])
        else:
            values = normalize_list_value(raw_value)
            if not values:
                continue

            text_values = [v for v in values if isinstance(v, str)]
            number_values = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            bool_values = [v for v in values if isinstance(v, bool)]

            matched_ids = set()

            if text_values:
                matched_ids.update(
                    value_qs.filter(value_text__in=text_values).values_list("product_id", flat=True)
                )

            if number_values:
                matched_ids.update(
                    value_qs.filter(value_number__in=number_values).values_list("product_id", flat=True)
                )

            if bool_values:
                matched_ids.update(
                    value_qs.filter(value_boolean__in=bool_values).values_list("product_id", flat=True)
                )

            queryset = queryset.filter(id__in=matched_ids).distinct()
            continue

        matched_ids = value_qs.values_list("product_id", flat=True).distinct()
        queryset = queryset.filter(id__in=matched_ids).distinct()

    return queryset.distinct()


# =========================================================
# Importer attributes
# data["importer_attributes"] = {
#   "param_id": ["A", "B"]
#   "param_id": {"min": 10, "max": 100}
#   "param_id": true
# }
# =========================================================

def apply_importer_attribute_filters(queryset, data, skip_param_id=None):
    importer_attrs = ensure_dict(data.get("importer_attributes", {}))

    if not importer_attrs:
        return queryset

    for param_id, raw_value in importer_attrs.items():
        if str(param_id) == str(skip_param_id):
            continue

        if raw_value in [None, "", []]:
            continue

        value_qs = ImporterParameterValue.objects.filter(
            parameter_id=param_id,
            parameter__is_filterable=True
        )

        range_value = normalize_range_value(raw_value)
        if range_value:
            if range_value["min"] is not None:
                value_qs = value_qs.filter(number_value__gte=range_value["min"])

            if range_value["max"] is not None:
                value_qs = value_qs.filter(number_value__lte=range_value["max"])
        else:
            values = normalize_list_value(raw_value)
            if not values:
                continue

            text_values = [v for v in values if isinstance(v, str)]
            number_values = [v for v in values if isinstance(v, (int, float)) and not isinstance(v, bool)]
            bool_values = [v for v in values if isinstance(v, bool)]

            matched_importer_ids = set()

            if text_values:
                matched_importer_ids.update(
                    value_qs.filter(text_value__in=text_values).values_list("importer_id", flat=True)
                )
                matched_importer_ids.update(
                    value_qs.filter(choice_value__value__in=text_values).values_list("importer_id", flat=True)
                )

            if number_values:
                matched_importer_ids.update(
                    value_qs.filter(number_value__in=number_values).values_list("importer_id", flat=True)
                )

            if bool_values:
                matched_importer_ids.update(
                    value_qs.filter(boolean_value__in=bool_values).values_list("importer_id", flat=True)
                )

            queryset = queryset.filter(importer_id__in=matched_importer_ids).distinct()
            continue

        matched_importer_ids = value_qs.values_list("importer_id", flat=True).distinct()
        queryset = queryset.filter(importer_id__in=matched_importer_ids).distinct()

    return queryset.distinct()


# =========================================================
# Main queryset builder
# =========================================================

def build_filtered_queryset(
    base_queryset,
    data,
    skip_static_keys=None,
    skip_attr_id=None,
    skip_custom_attr_id=None,
    skip_importer_attr_id=None
):
    skip_static_keys = skip_static_keys or set()
    qs = base_queryset

    if "category" not in skip_static_keys:
        qs = apply_category_filter(qs, data.get("category"))

    qs = apply_static_filters(qs, data, skip_keys=skip_static_keys)
    qs = apply_attribute_filters(qs, data, skip_attr_id=skip_attr_id)
    qs = apply_custom_attribute_filters(qs, data, skip_custom_attr_id=skip_custom_attr_id)
    qs = apply_importer_attribute_filters(qs, data, skip_param_id=skip_importer_attr_id)

    return qs.distinct()


# =========================================================
# Options builder
# =========================================================

def get_filter_options(base_queryset, data):
    selected_category_id = data.get("category")

    selected_brand = str(data.get("brand") or "")
    selected_country = str(data.get("country_of_manufacture") or "")
    selected_importer = str(data.get("importer") or "")
    selected_status = str(data.get("status") or "")
    selected_price_min = to_number(data.get("price_min"))
    selected_price_max = to_number(data.get("price_max"))

    selected_attributes = get_selected_map(data, "attributes")
    selected_custom_attributes = get_selected_map(data, "custom_attributes")
    selected_importer_attributes = get_selected_map(data, "importer_attributes")

    ancestor_category_ids = get_category_ancestor_ids(selected_category_id)

    category_scope_qs = get_category_scope_queryset(base_queryset, selected_category_id)

    price_scope_qs = build_filtered_queryset(
        category_scope_qs,
        data,
        skip_static_keys={"category", "price_min", "price_max"}
    )

    price_agg = price_scope_qs.aggregate(
        min_price=Min("price_min"),
        max_price=Max("price_max")
    )

    options = {
        "price": {
            "min": float(price_agg["min_price"]) if price_agg["min_price"] is not None else None,
            "max": float(price_agg["max_price"]) if price_agg["max_price"] is not None else None,
            "selected_min": selected_price_min,
            "selected_max": selected_price_max,
        },
        "brands": [],
        "countries": [],
        "importers": [],
        "statuses": [],
        "attributes": [],
        "custom_attributes": [],
        "importer_attributes": [],
    }

    # =====================================================
    # STATIC OPTIONS
    # =====================================================

    brand_qs = build_filtered_queryset(
        category_scope_qs,
        data,
        skip_static_keys={"category", "brand"}
    )
    active_brand_ids = set(
        brand_qs.exclude(brand_id__isnull=True).values_list("brand_id", flat=True).distinct()
    )
    all_brand_ids = set(
        category_scope_qs.exclude(brand_id__isnull=True).values_list("brand_id", flat=True).distinct()
    )

    for brand in Brand.objects.filter(id__in=all_brand_ids).order_by("name"):
        options["brands"].append({
            "id": str(brand.id),
            "name": brand.name,
            "active": brand.id in active_brand_ids,
            "selected": str(brand.id) == selected_brand,
        })

    country_qs = build_filtered_queryset(
        category_scope_qs,
        data,
        skip_static_keys={"category", "country_of_manufacture"}
    )
    active_country_ids = set(
        country_qs.exclude(country_of_manufacture_id__isnull=True).values_list("country_of_manufacture_id", flat=True).distinct()
    )
    all_country_ids = set(
        category_scope_qs.exclude(country_of_manufacture_id__isnull=True).values_list("country_of_manufacture_id", flat=True).distinct()
    )

    for country in Country.objects.filter(id__in=all_country_ids).order_by("name"):
        options["countries"].append({
            "id": str(country.id),
            "name": country.name,
            "active": country.id in active_country_ids,
            "selected": str(country.id) == selected_country,
        })

    importer_qs = build_filtered_queryset(
        category_scope_qs,
        data,
        skip_static_keys={"category", "importer"}
    )
    active_importer_ids = set(
        importer_qs.exclude(importer_id__isnull=True).values_list("importer_id", flat=True).distinct()
    )
    all_importer_ids = set(
        category_scope_qs.exclude(importer_id__isnull=True).values_list("importer_id", flat=True).distinct()
    )

    for importer in ImporterProfile.objects.filter(id__in=all_importer_ids).order_by("company_name"):
        options["importers"].append({
            "id": str(importer.id),
            "name": importer.company_name,
            "active": importer.id in active_importer_ids,
            "selected": str(importer.id) == selected_importer,
        })

    status_qs = build_filtered_queryset(
        category_scope_qs,
        data,
        skip_static_keys={"category", "status"}
    )
    active_statuses = set(status_qs.values_list("status", flat=True).distinct())

    for status_value, status_label in [
        ("available", "Առկա է"),
        ("on_order", "Պատվերով"),
    ]:
        options["statuses"].append({
            "value": status_value,
            "label": status_label,
            "active": status_value in active_statuses,
            "selected": status_value == selected_status,
        })

    # =====================================================
    # CATEGORY ATTRIBUTES OPTIONS
    # ancestor chain: 0 -> ... -> selected
    # =====================================================

    attributes = CategoryAttribute.objects.filter(
        category_id__in=ancestor_category_ids,
        is_main_filter=True
    ).select_related(
        "attribute_type",
        "category"
    ).order_by(
        "category__level",
        "attribute_type__name",
        "name"
    ).distinct()

    for attr in attributes:
        attr_qs = build_filtered_queryset(
            category_scope_qs,
            data,
            skip_static_keys={"category"},
            skip_attr_id=attr.id
        )

        attr_option = {
            "id": str(attr.id),
            "name": attr.name,
            "data_type": attr.data_type,
            "attribute_type": attr.attribute_type.name if attr.attribute_type else None,
            "values": [],
        }

        if attr.data_type in ["string", "select"]:
            all_values = ProductAttributeValue.objects.filter(
                product__in=category_scope_qs,
                attribute=attr
            ).exclude(
                value_text__isnull=True
            ).exclude(
                value_text=""
            ).values_list("value_text", flat=True).distinct()

            active_values = set(
                ProductAttributeValue.objects.filter(
                    product__in=attr_qs,
                    attribute=attr
                ).exclude(
                    value_text__isnull=True
                ).exclude(
                    value_text=""
                ).values_list("value_text", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_attributes.get(str(attr.id), []))

            for val in sorted(all_values):
                attr_option["values"].append({
                    "value": val,
                    "active": val in active_values,
                    "selected": val in selected_value,
                })

        elif attr.data_type == "number":
            all_values = ProductAttributeValue.objects.filter(
                product__in=category_scope_qs,
                attribute=attr
            ).exclude(
                value_number__isnull=True
            ).values_list("value_number", flat=True).distinct()

            active_values = set(
                ProductAttributeValue.objects.filter(
                    product__in=attr_qs,
                    attribute=attr
                ).exclude(
                    value_number__isnull=True
                ).values_list("value_number", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_attributes.get(str(attr.id), []))

            for val in sorted(all_values):
                float_val = float(val)
                attr_option["values"].append({
                    "value": float_val,
                    "active": val in active_values,
                    "selected": float_val in selected_value or val in selected_value,
                })

        elif attr.data_type == "boolean":
            all_values = ProductAttributeValue.objects.filter(
                product__in=category_scope_qs,
                attribute=attr
            ).exclude(
                value_boolean__isnull=True
            ).values_list("value_boolean", flat=True).distinct()

            active_values = set(
                ProductAttributeValue.objects.filter(
                    product__in=attr_qs,
                    attribute=attr
                ).exclude(
                    value_boolean__isnull=True
                ).values_list("value_boolean", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_attributes.get(str(attr.id), []))

            for val in all_values:
                attr_option["values"].append({
                    "value": val,
                    "label": "Այո" if val is True else "Ոչ",
                    "active": val in active_values,
                    "selected": val in selected_value,
                })

        options["attributes"].append(attr_option)

    # =====================================================
    # PRODUCT CUSTOM ATTRIBUTES OPTIONS
    # =====================================================

    all_custom_attr_ids = ProductCustomAttributeValue.objects.filter(
        product__in=category_scope_qs,
        attribute__is_main_filter=True
    ).values_list("attribute_id", flat=True).distinct()

    custom_attributes = ProductAttribute.objects.filter(
        id__in=all_custom_attr_ids,
        is_main_filter=True
    ).select_related("attribute_type").order_by("attribute_type__name", "name")

    for attr in custom_attributes:
        attr_qs = build_filtered_queryset(
            category_scope_qs,
            data,
            skip_static_keys={"category"},
            skip_custom_attr_id=attr.id
        )

        attr_option = {
            "id": str(attr.id),
            "name": attr.name,
            "data_type": attr.data_type,
            "attribute_type": attr.attribute_type.name if attr.attribute_type else None,
            "values": [],
        }

        if attr.data_type in ["string", "select"]:
            all_values = ProductCustomAttributeValue.objects.filter(
                product__in=category_scope_qs,
                attribute=attr
            ).exclude(
                value_text__isnull=True
            ).exclude(
                value_text=""
            ).values_list("value_text", flat=True).distinct()

            active_values = set(
                ProductCustomAttributeValue.objects.filter(
                    product__in=attr_qs,
                    attribute=attr
                ).exclude(
                    value_text__isnull=True
                ).exclude(
                    value_text=""
                ).values_list("value_text", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_custom_attributes.get(str(attr.id), []))

            for val in sorted(all_values):
                attr_option["values"].append({
                    "value": val,
                    "active": val in active_values,
                    "selected": val in selected_value,
                })

        elif attr.data_type == "number":
            all_values = ProductCustomAttributeValue.objects.filter(
                product__in=category_scope_qs,
                attribute=attr
            ).exclude(
                value_number__isnull=True
            ).values_list("value_number", flat=True).distinct()

            active_values = set(
                ProductCustomAttributeValue.objects.filter(
                    product__in=attr_qs,
                    attribute=attr
                ).exclude(
                    value_number__isnull=True
                ).values_list("value_number", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_custom_attributes.get(str(attr.id), []))

            for val in sorted(all_values):
                float_val = float(val)
                attr_option["values"].append({
                    "value": float_val,
                    "active": val in active_values,
                    "selected": float_val in selected_value or val in selected_value,
                })

        elif attr.data_type == "boolean":
            all_values = ProductCustomAttributeValue.objects.filter(
                product__in=category_scope_qs,
                attribute=attr
            ).exclude(
                value_boolean__isnull=True
            ).values_list("value_boolean", flat=True).distinct()

            active_values = set(
                ProductCustomAttributeValue.objects.filter(
                    product__in=attr_qs,
                    attribute=attr
                ).exclude(
                    value_boolean__isnull=True
                ).values_list("value_boolean", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_custom_attributes.get(str(attr.id), []))

            for val in all_values:
                attr_option["values"].append({
                    "value": val,
                    "label": "Այո" if val is True else "Ոչ",
                    "active": val in active_values,
                    "selected": val in selected_value,
                })

        options["custom_attributes"].append(attr_option)

    # =====================================================
    # IMPORTER ATTRIBUTES OPTIONS
    # =====================================================

    importer_ids_in_scope = set(
        category_scope_qs.exclude(importer_id__isnull=True).values_list("importer_id", flat=True).distinct()
    )

    all_param_ids = ImporterParameterValue.objects.filter(
        importer_id__in=importer_ids_in_scope,
        parameter__is_filterable=True
    ).values_list("parameter_id", flat=True).distinct()

    importer_params = ImporterParameter.objects.filter(
        id__in=all_param_ids,
        is_filterable=True
    ).select_related("parameter_type").order_by("parameter_type__name", "name")

    for param in importer_params:
        param_qs = build_filtered_queryset(
            category_scope_qs,
            data,
            skip_static_keys={"category"},
            skip_importer_attr_id=param.id
        )
        importer_ids_in_param_qs = set(
            param_qs.exclude(importer_id__isnull=True).values_list("importer_id", flat=True).distinct()
        )

        param_option = {
            "id": str(param.id),
            "name": param.name,
            "value_type": param.value_type,
            "parameter_type": param.parameter_type.name if param.parameter_type else None,
            "values": [],
        }

        if param.value_type in ["text", "choice"]:
            all_text_values = ImporterParameterValue.objects.filter(
                importer_id__in=importer_ids_in_scope,
                parameter=param
            ).exclude(
                text_value__isnull=True
            ).exclude(
                text_value=""
            ).values_list("text_value", flat=True).distinct()

            all_choice_values = ImporterParameterValue.objects.filter(
                importer_id__in=importer_ids_in_scope,
                parameter=param
            ).exclude(
                choice_value__isnull=True
            ).values_list("choice_value__value", flat=True).distinct()

            all_values = set(all_text_values) | set(all_choice_values)

            active_text_values = set(
                ImporterParameterValue.objects.filter(
                    importer_id__in=importer_ids_in_param_qs,
                    parameter=param
                ).exclude(
                    text_value__isnull=True
                ).exclude(
                    text_value=""
                ).values_list("text_value", flat=True).distinct()
            )

            active_choice_values = set(
                ImporterParameterValue.objects.filter(
                    importer_id__in=importer_ids_in_param_qs,
                    parameter=param
                ).exclude(
                    choice_value__isnull=True
                ).values_list("choice_value__value", flat=True).distinct()
            )

            active_values = active_text_values | active_choice_values
            selected_value = normalize_list_value(selected_importer_attributes.get(str(param.id), []))

            for val in sorted(all_values):
                param_option["values"].append({
                    "value": val,
                    "active": val in active_values,
                    "selected": val in selected_value,
                })

        elif param.value_type == "number":
            all_values = ImporterParameterValue.objects.filter(
                importer_id__in=importer_ids_in_scope,
                parameter=param
            ).exclude(
                number_value__isnull=True
            ).values_list("number_value", flat=True).distinct()

            active_values = set(
                ImporterParameterValue.objects.filter(
                    importer_id__in=importer_ids_in_param_qs,
                    parameter=param
                ).exclude(
                    number_value__isnull=True
                ).values_list("number_value", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_importer_attributes.get(str(param.id), []))

            for val in sorted(all_values):
                float_val = float(val)
                param_option["values"].append({
                    "value": float_val,
                    "active": val in active_values,
                    "selected": float_val in selected_value or val in selected_value,
                })

        elif param.value_type == "boolean":
            all_values = ImporterParameterValue.objects.filter(
                importer_id__in=importer_ids_in_scope,
                parameter=param
            ).exclude(
                boolean_value__isnull=True
            ).values_list("boolean_value", flat=True).distinct()

            active_values = set(
                ImporterParameterValue.objects.filter(
                    importer_id__in=importer_ids_in_param_qs,
                    parameter=param
                ).exclude(
                    boolean_value__isnull=True
                ).values_list("boolean_value", flat=True).distinct()
            )

            selected_value = normalize_list_value(selected_importer_attributes.get(str(param.id), []))

            for val in all_values:
                param_option["values"].append({
                    "value": val,
                    "label": "Առկա է" if val is True else "Առկա չէ",
                    "active": val in active_values,
                    "selected": val in selected_value,
                })

        options["importer_attributes"].append(param_option)

    return options