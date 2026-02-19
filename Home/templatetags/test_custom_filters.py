from django.test import TestCase
from django import template
from django.template import Context
from django.forms import CharField, TextInput
from django.db import models
import re

class CustomFiltersTestCase(TestCase):
    def setUp(self):
        self.t = template.Template("{% load custom_filters %}")
        self.ctx = Context()
        self.field = CharField(widget=TextInput())

    def test_add_class_happy_path(self):
        rendered = self.t.render(self.ctx)
        html = self.field.as_widget(attrs={"class": "test-class"})
        result = template.base.add_class(self.field, "test-class")
        self.assertIn('class="test-class"', str(result))

    def test_add_class_empty_class(self):
        result = template.base.add_class(self.field, "")
        self.assertIn('class=""', str(result))

    def test_add_class_invalid_field(self):
        with self.assertRaises(AttributeError):
            template.base.add_class(None, "test-class")

    def test_get_item_happy_path(self):
        test_dict = {"key": "value"}
        result = template.base.get_item(test_dict, "key")
        self.assertEqual(result, "value")

    def test_get_item_missing_key(self):
        test_dict = {"key": "value"}
        result = template.base.get_item(test_dict, "missing_key")
        self.assertEqual(result, "")

    def test_get_item_none_dictionary(self):
        result = template.base.get_item(None, "key")
        self.assertIsNone(result)

    def test_multiply_happy_path(self):
        result = template.base.multiply(5, 2)
        self.assertEqual(result, 10.0)

    def test_multiply_string_numbers(self):
        result = template.base.multiply("5", "2")
        self.assertEqual(result, 10.0)

    def test_multiply_invalid_input(self):
        result = template.base.multiply("five", 2)
        self.assertEqual(result, 0)

    def test_mul_happy_path(self):
        result = template.base.mul(5, 2)
        self.assertEqual(result, 10.0)

    def test_mul_string_numbers(self):
        result = template.base.mul("5", "2")
        self.assertEqual(result, 10.0)

    def test_mul_invalid_input(self):
        result = template.base.mul("five", 2)
        self.assertEqual(result, 0)

    def test_div_happy_path(self):
        result = template.base.div(10, 2)
        self.assertEqual(result, 5.0)

    def test_div_division_by_zero(self):
        result = template.base.div(10, 0)
        self.assertEqual(result, 0)

    def test_div_invalid_input(self):
        result = template.base.div("ten", 2)
        self.assertEqual(result, 0)

    def test_divide_happy_path(self):
        result = template.base.divide(10, 2)
        self.assertEqual(result, 5.0)

    def test_divide_division_by_zero(self):
        result = template.base.divide(10, 0)
        self.assertEqual(result, 0)

    def test_divide_invalid_input(self):
        result = template.base.divide("ten", 2)
        self.assertEqual(result, 0)

    def test_percentage_happy_path(self):
        result = template.base.percentage(50, 200)
        self.assertEqual(result, 25.0)

    def test_percentage_division_by_zero(self):
        result = template.base.percentage(50, 0)
        self.assertEqual(result, 0)

    def test_percentage_invalid_input(self):
        result = template.base.percentage("fifty", 200)
        self.assertEqual(result, 0)

    def test_to_int_happy_path(self):
        result = template.base.to_int(5.7)
        self.assertEqual(result, 5)

    def test_to_int_string_number(self):
        result = template.base.to_int("5")
        self.assertEqual(result, 5)

    def test_to_int_invalid_input(self):
        result = template.base.to_int("five")
        self.assertEqual(result, 0)

    class TestModel(models.Model):
        status = models.CharField(max_length=20)
        name = models.CharField(max_length=100)

        class Meta:
            app_label = 'custom_filters'

    def test_findall_happy_path(self):
        queryset = [
            self.TestModel(status="present", name="Alice"),
            self.TestModel(status="absent", name="Bob"),
            self.TestModel(status="present", name="Charlie")
        ]
        result = template.base.findall(queryset, "status,present")
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].name, "Alice")
        self.assertEqual(result[1].name, "Charlie")

    def test_findall_no_matches(self):
        queryset = [
            self.TestModel(status="absent", name="Alice"),
            self.TestModel(status="absent", name="Bob")
        ]
        result = template.base.findall(queryset, "status,present")
        self.assertEqual(len(result), 0)

    def test_findall_invalid_pair_format(self):
        queryset = [self.TestModel(status="present", name="Alice")]
        with self.assertRaises(ValueError):
            template.base.findall(queryset, "status-present")

    def test_findall_nonexistent_attribute(self):
        queryset = [self.TestModel(status="present", name="Alice")]
        result = template.base.findall(queryset, "nonexistent,present")
        self.assertEqual(len(result), 0)