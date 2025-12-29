from django.utils import timezone
from .models import PromotionEvent
from decimal import Decimal

class PromotionEngine:
    @staticmethod
    def calculate_best_price(product, quantity=1):
        """
        Input: Product, Quantity
        Output: (final_price, applied_rule, original_price)
        
        Logic:
        1. Tìm tất cả các sự kiện đang Active
        2. Tìm tất cả các Rule thuộc sự kiện đó apply cho Product này
        3. Chọn Rule giảm giá tốt nhất (Giá cuối cùng thấp nhất)
        """
        now = timezone.now()
        original_price = product.price
        
        """1. Tìm tất cả các sự kiện đang Active """
        active_events = PromotionEvent.objects.filter(
             is_active=True, 
             start_date__lte=now, 
             end_date__gte=now
        )
        
        if not active_events.exists():
             return original_price, None, original_price
             
        # 2. Tìm tất cả các Rule thuộc sự kiện đó apply cho Product này
        valid_rules = []
        for event in active_events:
             # Lấy các rules của event
             # Filter rules mà product nằm trong danh sách products
             # Optimisation: Có thể query DB trực tiếp thay vì loop nếu data lớn
             # rule.products.all() check
             
             # Query optimize:
             rules_for_product = event.rules.filter(products=product)
             
             for rule in rules_for_product:
                 if quantity >= rule.min_quantity:
                     valid_rules.append(rule)
        
        if not valid_rules:
             return original_price, None, original_price
             
        # 3. Chọn Rule giảm giá tốt nhất (Giá cuối cùng thấp nhất)
        best_price = original_price
        best_rule = None
        
        for rule in valid_rules:
             discount_amt = rule.calculate_discount(original_price, quantity)
             potential_price = max(Decimal(0), original_price - discount_amt)
             
             # So sánh: chọn giá thấp nhất
             if potential_price < best_price:
                 best_price = potential_price
                 best_rule = rule
                 
        return best_price, best_rule, original_price

    @staticmethod
    def calculate_cart_totals(cart_items):
        total_original = 0
        total_discounted = 0
        details = []

        for item in cart_items:
            final_price, rule, original_price = PromotionEngine.calculate_best_price(item.product, item.quantity)
            
            line_total_original = original_price * item.quantity
            line_total_discounted = final_price * item.quantity
            
            total_original += line_total_original
            total_discounted += line_total_discounted
            
            details.append({
                'item_id': item.id,
                'product': item.product,
                'quantity': item.quantity,
                'original_single_price': original_price,
                'final_single_price': final_price,
                'applied_rule': rule,
                'line_total': line_total_discounted
            })
            
        return {
            'total_original': total_original,
            'total_final': total_discounted,
            'total_discount_amount': total_original - total_discounted,
            'items_details': details
        }
