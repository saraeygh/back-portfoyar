from rest_framework import serializers
from global_market.models import GlobalRelation


class GlobalRelatedStockSerailizer(serializers.ModelSerializer):
    ins_code = serializers.SerializerMethodField()

    class Meta:
        model = GlobalRelation
        fields = [
            "id",
            "ins_code",
        ]

    def get_ins_code(self, instance: GlobalRelation):
        ins_code = instance.stock_instrument.ins_code

        return ins_code
