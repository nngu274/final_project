"""
Employee Dashboard Page
Handles all employee workflow UI components
"""
import streamlit as st
from services.employee_service import calculate_low_stock, record_sale

class EmployeeDashboard:
    """Employee dashboard with catalog viewing, sales logging, and training."""

    def __init__(self, products, sales_log, products_path, sales_path, save_json_func):
        """
        Initialize employee dashboard.

        Args:
            products (list): Product inventory data
            sales_log (list): Sales transaction log
            products_path (Path): Path to products JSON file
            sales_path (Path): Path to sales JSON file
            save_json_func (callable): Function to save JSON data
        """
        self.products = products
        self.sales_log = sales_log
        self.products_path = products_path
        self.sales_path = sales_path
        self.save_json = save_json_func

    def render(self):
        """Render the complete employee dashboard."""
        st.header("Employee Dashboard")

        # Contextual help system
        self._render_contextual_help()

        st.divider()

        # Display key metrics
        self._render_metrics()

        st.divider()

        # Create tabs for different employee functions
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "View Catalog",
            "Log Sales",
            "Flag Low Stock",
            "Training",
            "Analytics",
            "Alerts",
            "AI Assistant"
        ])

        with tab1:
            self._render_catalog_tab()

        with tab2:
            self._render_sales_tab()

        with tab3:
            self._render_low_stock_tab()

        with tab4:
            self._render_training_tab()

        with tab5:
            self._render_analytics_tab()

        with tab6:
            self._render_alerts_tab()

        with tab7:
            self._render_ai_assistant_tab()

    def _render_contextual_help(self):
        """Render contextual help based on current tab."""
        # Get current tab from session state or default to first tab
        current_tab = st.session_state.get("employee_current_tab", 0)

        help_content = {
            0: {  # Catalog
                "title": "Catalog Search & Filter",
                "content": """
                **🔍 Search Tips:**
                - Use keywords to find products by name
                - Search is case-insensitive and matches partial names

                **🏷️ Filter Options:**
                - Filter by category to see related products
                - Filter by shelf location for physical store navigation
                - Combine search and filters for precise results

                **📊 Sort Options:**
                - Sort by stock levels to prioritize low inventory
                - Sort by price to find affordable or premium items
                """
            },
            1: {  # Sales
                "title": "Sales Logging Best Practices",
                "content": """
                **✅ Before Recording:**
                - Verify current stock levels
                - Double-check product selection
                - Confirm quantities are accurate

                **💰 Quantity Selection:**
                - Use presets for common quantities (1, 5, 10)
                - Switch to custom for other amounts
                - System prevents selling more than available stock

                **📝 Notes Field:**
                - Add customer special requests
                - Note any issues or circumstances
                - Include relevant context for management
                """
            },
            2: {  # Low Stock
                "title": "Stock Monitoring Guidelines",
                "content": """
                **⚠️ Low Stock Threshold:**
                - Items with ≤5 units are flagged
                - Critical items (≤2 units) need immediate attention
                - Out of stock items require urgent restocking

                **🚨 Action Required:**
                - Notify shop owner of critical low stock
                - Check for fast-selling items in Analytics tab
                - Monitor trends to prevent future stockouts
                """
            },
            3: {  # Training
                "title": "Training & Certification",
                "content": """
                **📚 Learning Path:**
                - Start with guidelines and acknowledge reading
                - Take the knowledge quiz to test understanding
                - Achieve 80%+ to pass and earn certification

                **🎯 Quiz Tips:**
                - Read all questions carefully
                - Review explanations for incorrect answers
                - Retake quiz if needed to improve score

                **🏆 Achievements:**
                - Earn badges for completed modules
                - Track progress in your profile
                - Higher scores unlock advanced training
                """
            },
            4: {  # Analytics
                "title": "Understanding Your Performance",
                "content": """
                **📊 Key Metrics:**
                - Today's sales vs overall performance
                - Average sale value helps identify trends
                - Top products show customer preferences

                **📈 Sales Activity:**
                - Recent transactions show latest activity
                - Product performance highlights bestsellers
                - Revenue tracking supports business decisions

                **💡 Insights:**
                - Use data to optimize inventory
                - Identify peak selling times
                - Focus on high-performing products
                """
            },
            5: {  # Alerts
                "title": "Alert Management System",
                "content": """
                **🚨 Alert Types:**
                - **Critical**: Out of stock or very low items
                - **Warning**: Items running low (3-5 units)
                - **Info**: Fast-selling products, trends

                **⚡ Quick Actions:**
                - Mark alerts as read when addressed
                - Report issues directly to management
                - Use alerts to prioritize restocking tasks

                **📋 Best Practices:**
                - Check alerts at start of shift
                - Address critical alerts immediately
                - Keep management informed of issues
                """
            }
        }

        # Help toggle
        if st.checkbox("💡 Show Help", key="show_help", value=False):
            help_info = help_content.get(current_tab, help_content[0])
            with st.expander(f"Help: {help_info['title']}", expanded=True):
                st.markdown(help_info["content"])

        # Update current tab in session state (this would be set when tabs change)
        # For now, we'll use a simplified approach

    def _render_metrics(self):
        """Render dashboard metrics with enhanced visuals."""
        # Calculate metrics
        low_stock_count = len([p for p in self.products if p.get("stock", 0) <= 5])
        total_stock = sum([p.get("stock", 0) for p in self.products])
        sales_count = len(self.sales_log)
        total_revenue = self._calculate_total_revenue()

        # Enhanced metrics display with status indicators
        st.write("### 📊 Dashboard Overview")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            status = "🟢" if len(self.products) > 0 else "🔴"
            st.metric(
                "Products Available",
                len(self.products),
                help="Total number of products in catalog"
            )

        with col2:
            status = "🔴" if low_stock_count > 2 else "🟡" if low_stock_count > 0 else "🟢"
            st.metric(
                "Low Stock Items",
                low_stock_count,
                delta=f"{status}",
                help="Products with ≤5 units remaining"
            )

        with col3:
            st.metric(
                "Sales Logged",
                sales_count,
                help="Total sales transactions recorded"
            )

        with col4:
            avg_sale = total_revenue / max(sales_count, 1)
            st.metric(
                "Avg Sale Value",
                f"${avg_sale:.2f}",
                help="Average revenue per sale"
            )

        # Quick status summary
        if low_stock_count > 0:
            st.warning(f"⚠️ {low_stock_count} products need restocking attention.")
        else:
            st.success("✅ All products are well-stocked!")

    def _render_catalog_tab(self):
        """Render the enhanced catalog viewing tab with search and filter."""
        st.subheader("📦 Product Catalog")

        if not self.products:
            st.info("No products available.")
            return

        # Search and filter controls
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            search_query = st.text_input(
                "🔍 Search products",
                placeholder="Enter product name...",
                key="catalog_search",
                help="Search by product name"
            )

        with col2:
            # Get unique categories
            categories = ["All"] + sorted(list(set(p.get("category", "Uncategorized") for p in self.products)))
            category_filter = st.selectbox(
                "Category",
                categories,
                key="catalog_category_filter",
                help="Filter by product category"
            )

        with col3:
            # Get unique shelves
            shelves = ["All"] + sorted(list(set(p.get("shelf", "Unassigned") for p in self.products)))
            shelf_filter = st.selectbox(
                "Shelf",
                shelves,
                key="catalog_shelf_filter",
                help="Filter by shelf location"
            )

        # Sort options
        sort_options = ["Name (A-Z)", "Name (Z-A)", "Price (Low-High)", "Price (High-Low)", "Stock (Low-High)", "Stock (High-Low)"]
        sort_by = st.selectbox(
            "Sort by",
            sort_options,
            key="catalog_sort",
            help="Sort products by selected criteria"
        )

        # Filter products based on search and filters
        filtered_products = self._filter_products(search_query, category_filter, shelf_filter)

        # Sort products
        filtered_products = self._sort_products(filtered_products, sort_by)

        # Display results count
        st.write(f"Showing {len(filtered_products)} of {len(self.products)} products")

        if filtered_products:
            # Display products in enhanced table format
            display_data = []
            for product in filtered_products:
                display_data.append({
                    "Name": product["name"],
                    "Category": product.get("category", "N/A"),
                    "Price": f"${product.get('price', 0):.2f}",
                    "Stock": product.get("stock", 0),
                    "Shelf": product.get("shelf", "N/A"),
                    "Status": "⚠️ Low Stock" if product.get("stock", 0) <= 5 else "✅ In Stock"
                })

            # Use container width and add some styling
            st.dataframe(
                display_data,
                use_container_width=True,
                column_config={
                    "Status": st.column_config.TextColumn("Status", width="small")
                }
            )

            # Show low stock summary if any
            low_stock_count = len([p for p in filtered_products if p.get("stock", 0) <= 5])
            if low_stock_count > 0:
                st.info(f"📊 {low_stock_count} products in current view are low on stock (≤5 units)")

        else:
            st.info("No products match your search criteria. Try adjusting your filters.")

    def _filter_products(self, search_query, category_filter, shelf_filter):
        """Filter products based on search query and filters."""
        filtered = self.products.copy()

        # Apply search filter
        if search_query:
            search_lower = search_query.lower()
            filtered = [p for p in filtered if search_lower in p.get("name", "").lower()]

        # Apply category filter
        if category_filter != "All":
            filtered = [p for p in filtered if p.get("category", "Uncategorized") == category_filter]

        # Apply shelf filter
        if shelf_filter != "All":
            filtered = [p for p in filtered if p.get("shelf", "Unassigned") == shelf_filter]

        return filtered

    def _sort_products(self, products, sort_by):
        """Sort products based on selected criteria."""
        if sort_by == "Name (A-Z)":
            return sorted(products, key=lambda x: x.get("name", "").lower())
        elif sort_by == "Name (Z-A)":
            return sorted(products, key=lambda x: x.get("name", "").lower(), reverse=True)
        elif sort_by == "Price (Low-High)":
            return sorted(products, key=lambda x: x.get("price", 0))
        elif sort_by == "Price (High-Low)":
            return sorted(products, key=lambda x: x.get("price", 0), reverse=True)
        elif sort_by == "Stock (Low-High)":
            return sorted(products, key=lambda x: x.get("stock", 0))
        elif sort_by == "Stock (High-Low)":
            return sorted(products, key=lambda x: x.get("stock", 0), reverse=True)
        else:
            return products

    def _render_sales_tab(self):
        """Render the enhanced sales logging tab with confirmation."""
        st.subheader("💰 Log Daily Sales")

        if not self.products:
            st.info("No products available to sell.")
            return

        # Check for low stock warnings
        low_stock_items = calculate_low_stock(self.products)
        if low_stock_items:
            with st.expander("⚠️ Low Stock Alert", expanded=False):
                st.warning("The following items are running low:")
                for item in low_stock_items:
                    st.write(f"• **{item['name']}**: {item['stock']} units remaining")

        # Enhanced sales form using Streamlit form
        with st.form("enhanced_sale_form", clear_on_submit=True):
            st.write("### Record New Sale")

            # Product selection
            product_names = [p["name"] for p in self.products]
            selected_product_name = st.selectbox(
                "Select Product",
                product_names,
                key="sale_product_select",
                help="Choose the product that was sold"
            )

            # Get selected product details
            selected_product = next((p for p in self.products if p["name"] == selected_product_name), None)

            if selected_product:
                # Display current stock prominently
                current_stock = selected_product.get("stock", 0)
                col1, col2, col3 = st.columns(3)
                col1.metric("Current Stock", current_stock)
                col2.metric("Price per Unit", f"${selected_product.get('price', 0):.2f}")
                col3.metric("Category", selected_product.get("category", "N/A"))

                # Quantity selection with presets
                st.write("**Quantity Sold**")
                quantity_preset = st.radio(
                    "Quick Select",
                    ["1", "2", "5", "10", "Custom"],
                    index=0,
                    horizontal=True,
                    label_visibility="collapsed",
                    key="quantity_preset"
                )

                if quantity_preset == "Custom":
                    max_qty = min(current_stock, 100)  # Reasonable limit
                    quantity = st.number_input(
                        "Custom Quantity",
                        min_value=1,
                        max_value=max_qty,
                        value=1,
                        step=1,
                        key="custom_quantity",
                        help=f"Enter quantity (1-{max_qty})"
                    )
                else:
                    quantity = int(quantity_preset)

                # Optional notes
                notes = st.text_area(
                    "Notes (Optional)",
                    height=60,
                    placeholder="Add any special notes about this sale...",
                    key="sale_notes",
                    help="Customer requests, special circumstances, etc."
                )

                # Sale summary
                total_value = quantity * selected_product.get("price", 0)
                st.write("---")
                st.write("**Sale Summary**")
                summary_col1, summary_col2 = st.columns(2)
                summary_col1.write(f"• {quantity} × {selected_product_name}")
                summary_col2.write(f"• Total: **${total_value:.2f}**")

                # Stock warning if applicable
                if quantity > current_stock:
                    st.error(f"❌ Cannot sell {quantity} units. Only {current_stock} available.")
                elif current_stock - quantity <= 5:
                    st.warning(f"⚠️ This sale will leave only {current_stock - quantity} units remaining.")

                # Confirmation checkbox
                confirm_sale = st.checkbox(
                    "✅ I confirm this sale information is correct",
                    key="sale_confirmation",
                    help="Please verify all details before submitting"
                )

                # Submit button
                submit_disabled = not confirm_sale or quantity > current_stock
                submitted = st.form_submit_button(
                    "📝 Record Sale",
                    type="primary",
                    disabled=submit_disabled,
                    use_container_width=True
                )

                if submitted and confirm_sale:
                    self._handle_sale_recording(selected_product_name, quantity, notes)

    def _handle_sale_recording(self, product_name, quantity_sold, notes=""):
        """Handle the sale recording process with enhanced feedback and loading states."""
        # Show loading state
        with st.spinner("Recording sale..."):
            import time
            time.sleep(0.5)  # Brief delay to show loading state

            try:
                success, message = record_sale(
                    self.products,
                    self.sales_log,
                    product_name,
                    quantity_sold
                )

                if success:
                    # Save updated data
                    self.save_json(self.products_path, self.products)
                    self.save_json(self.sales_path, self.sales_log)

                    # Enhanced success message
                    product_info = next((p for p in self.products if p["name"] == product_name), {})
                    total_value = quantity_sold * product_info.get("price", 0)
                    remaining_stock = product_info.get("stock", 0)

                    st.success("✅ Sale recorded successfully!")
                    st.write(f"• **{quantity_sold}× {product_name}** - ${total_value:.2f}")
                    st.write(f"• Remaining stock: **{remaining_stock}** units")

                    if notes:
                        st.info(f"📝 Note: {notes}")

                    # Check if this created a low stock situation
                    if remaining_stock <= 5:
                        st.warning("⚠️ This item is now low on stock. Consider restocking soon.")

                    # Auto-refresh to update metrics
                    time.sleep(2)  # Brief pause to show success message
                    st.rerun()
                else:
                    st.error(f"❌ Sale recording failed: {message}")
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
                st.info("Please try again or contact support if the problem persists.")

    def _render_low_stock_tab(self):
        """Render the low stock monitoring tab."""
        st.subheader("Flag Items Running Dangerously Low")

        low_items = calculate_low_stock(self.products)
        if low_items:
            st.warning("The following items need attention:")
            for item in low_items:
                st.error(f"**{item['name']}** is low on stock. Only {item['stock']} units remaining.")
        else:
            st.success("✅ No low-stock items right now. Inventory is well-stocked!")

    def _render_training_tab(self):
        """Render the interactive training tab with quiz and progress tracking."""
        st.subheader("🎓 Employee Training Center")

        # Training tabs for different modules
        training_tabs = st.tabs(["📚 Guidelines", "🎯 Knowledge Quiz", "📈 Progress", "🏆 Achievements"])

        with training_tabs[0]:
            self._render_training_guidelines()

        with training_tabs[1]:
            self._render_training_quiz()

        with training_tabs[2]:
            self._render_training_progress()

        with training_tabs[3]:
            self._render_training_achievements()

    def _render_training_guidelines(self):
        """Render the training guidelines section."""
        st.markdown("""
        ### 🥖 Bakery Basics - Essential Guidelines

        **📦 Inventory Management:**
        - Always rotate stock using **first-in, first-out** (FIFO) method
        - Check expiration dates daily and remove expired items
        - Keep display shelves neat, labeled, and visually appealing

        **💰 Sales Procedures:**
        - Record sales accurately at the end of each shift
        - Double-check quantities before recording transactions
        - Report any discrepancies to the Shop Owner immediately

        **⚠️ Stock Monitoring:**
        - Flag low-stock items before they run out
        - Alert Shop Owner when items drop below 5 units
        - Help maintain optimal inventory levels

        **🧹 Maintenance & Safety:**
        - Report damaged or stale products to the Shop Owner
        - Maintain cleanliness in display and storage areas
        - Follow all health and safety guidelines

        **💡 Pro Tips:**
        - Familiarize yourself with product locations and pricing
        - Be helpful and knowledgeable with customer inquiries
        - Teamwork makes the dream work! 🤝
        """)

        # Acknowledgment checkbox
        if st.checkbox("✅ I have read and understood the training guidelines", key="guidelines_ack"):
            st.success("🎉 Guidelines reviewed! Ready for the quiz?")
            if st.button("Take the Knowledge Quiz", type="primary"):
                st.session_state["training_active_tab"] = 1  # Switch to quiz tab
                st.rerun()
        else:
            st.info("📖 Please read through all guidelines and check the box when done.")

    def _render_training_quiz(self):
        """Render the interactive knowledge quiz."""
        st.markdown("### 🧠 Knowledge Check")

        # Initialize quiz state if not exists
        if "quiz_answers" not in st.session_state:
            st.session_state["quiz_answers"] = {}
        if "quiz_submitted" not in st.session_state:
            st.session_state["quiz_submitted"] = False

        # Quiz questions
        questions = [
            {
                "question": "What does FIFO stand for in inventory management?",
                "options": ["First In, First Out", "Fast Inventory Flow Only", "Food Inventory First Order", "Final Inventory Full Order"],
                "correct": 0,
                "explanation": "FIFO (First In, First Out) ensures older stock is used before newer stock to maintain freshness."
            },
            {
                "question": "When should you alert the Shop Owner about low stock?",
                "options": ["When items reach 10 units", "When items reach 5 units or below", "When items are completely out", "Never, they check automatically"],
                "correct": 1,
                "explanation": "Items should be flagged when they drop to 5 units or below to prevent stockouts."
            },
            {
                "question": "What should you do if you notice expired products?",
                "options": ["Sell them at discount", "Remove them immediately and report to owner", "Leave them for the owner to handle", "Mix them with fresh products"],
                "correct": 1,
                "explanation": "Expired products must be removed immediately for safety and quality reasons."
            },
            {
                "question": "How should sales be recorded?",
                "options": ["At the end of the week only", "Immediately after each transaction", "Whenever you remember", "Only for large sales"],
                "correct": 1,
                "explanation": "Sales should be recorded immediately to maintain accurate inventory and sales tracking."
            },
            {
                "question": "What is the most important aspect of customer service?",
                "options": ["Fast service only", "Friendly and knowledgeable assistance", "Only taking orders", "Cleaning the display"],
                "correct": 1,
                "explanation": "Being helpful and knowledgeable creates positive customer experiences and encourages repeat business."
            }
        ]

        # Display questions
        for i, q in enumerate(questions):
            st.write(f"**Question {i+1}:** {q['question']}")

            # Get user's answer
            answer_key = f"quiz_q_{i}"
            answer = st.radio(
                f"Select your answer for question {i+1}:",
                q["options"],
                index=None,
                key=answer_key,
                label_visibility="collapsed"
            )

            # Store answer
            if answer is not None:
                st.session_state["quiz_answers"][i] = q["options"].index(answer)

            st.write("---")

        # Submit button
        if st.button("Submit Quiz", type="primary", use_container_width=True):
            st.session_state["quiz_submitted"] = True
            st.rerun()

        # Show results if submitted
        if st.session_state["quiz_submitted"]:
            self._show_quiz_results(questions)

    def _show_quiz_results(self, questions):
        """Display quiz results and handle scoring."""
        answers = st.session_state["quiz_answers"]
        correct_count = 0
        total_questions = len(questions)

        st.markdown("### 📊 Quiz Results")

        # Calculate score
        for i, q in enumerate(questions):
            user_answer = answers.get(i)
            is_correct = user_answer == q["correct"]

            if is_correct:
                correct_count += 1
                st.success(f"✅ Question {i+1}: Correct")
            else:
                st.error(f"❌ Question {i+1}: Incorrect")
                st.info(f"**Correct answer:** {q['options'][q['correct']]}")
                st.write(f"*{q['explanation']}*")

        # Final score
        score_percentage = (correct_count / total_questions) * 100

        st.write("---")
        st.metric("Your Score", f"{correct_count}/{total_questions}", f"{score_percentage:.1f}%")

        if score_percentage >= 80:
            st.success("🎉 Congratulations! You passed the training quiz!")
            st.balloons()

            # Record completion
            if st.button("Complete Training Module", type="primary"):
                self._record_training_completion("basic_training", score_percentage)
                st.success("✅ Training module completed! Check your progress tab.")
                st.rerun()
        else:
            st.warning("📚 You need 80% or higher to pass. Please review the guidelines and try again.")
            if st.button("Retake Quiz"):
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False
                st.rerun()

    def _record_training_completion(self, module_name, score):
        """Record training completion in session state."""
        if "training_progress" not in st.session_state:
            st.session_state["training_progress"] = {}

        st.session_state["training_progress"][module_name] = {
            "completed": True,
            "score": score,
            "date": "2026-05-12",  # Current date
            "badge": "🥖 Basic Training"
        }

    def _render_training_progress(self):
        """Render training progress tracking."""
        st.markdown("### 📈 Your Training Progress")

        progress = st.session_state.get("training_progress", {})

        if not progress:
            st.info("No training modules completed yet. Start with the guidelines and quiz!")
            return

        # Progress overview
        completed_modules = len([m for m in progress.values() if m.get("completed")])
        total_modules = 5  # Could be expanded

        col1, col2 = st.columns(2)
        col1.metric("Modules Completed", completed_modules)
        col2.metric("Overall Progress", f"{(completed_modules/total_modules)*100:.0f}%")

        # Progress bar
        st.progress(completed_modules / total_modules)

        # Completed modules list
        st.write("**Completed Modules:**")
        for module_name, data in progress.items():
            if data.get("completed"):
                st.write(f"✅ **{data.get('badge', module_name)}** - Score: {data.get('score', 0):.1f}% ({data.get('date', 'N/A')})")

        # Next steps
        if completed_modules < total_modules:
            st.info("Keep learning! More advanced training modules coming soon.")

    def _render_training_achievements(self):
        """Render training achievements and badges."""
        st.markdown("### 🏆 Training Achievements")

        progress = st.session_state.get("training_progress", {})

        if not progress:
            st.info("Complete your first training module to earn your first badge!")
            return

        # Achievement badges
        achievements = []

        for module_name, data in progress.items():
            if data.get("completed"):
                score = data.get("score", 0)
                if score >= 90:
                    achievements.append(("🏆 Expert Baker", "Scored 90%+ on training"))
                elif score >= 80:
                    achievements.append(("🥖 Trained Staff", "Passed basic training"))

        if achievements:
            for badge, description in achievements:
                col1, col2 = st.columns([1, 3])
                col1.write(badge)
                col2.write(f"**{description}**")
                st.write("---")
        else:
            st.write("No achievements yet. Complete training modules to earn badges!")

    def _render_analytics_tab(self):
        """Render the sales analytics dashboard."""
        st.subheader("📊 Sales Analytics")

        if not self.sales_log:
            st.info("No sales data available yet. Start logging sales to see analytics!")
            return

        # Analytics metrics
        self._render_analytics_metrics()

        st.divider()

        # Charts and insights
        self._render_sales_charts()

    def _render_analytics_metrics(self):
        """Render key analytics metrics."""
        # Calculate metrics
        total_sales = len(self.sales_log)
        total_quantity = sum(sale.get("quantity_sold", 0) for sale in self.sales_log)
        total_revenue = self._calculate_total_revenue()

        # Today's metrics (simplified - in real app would filter by date)
        today_sales = len([s for s in self.sales_log if self._is_today(s.get("timestamp", ""))])
        today_quantity = sum(s.get("quantity_sold", 0) for s in self.sales_log if self._is_today(s.get("timestamp", "")))
        today_revenue = self._calculate_revenue_for_period(lambda s: self._is_today(s.get("timestamp", "")))

        # Display metrics
        st.write("### Today's Performance")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Sales Today", today_sales)
        col2.metric("Items Sold Today", today_quantity)
        col3.metric("Revenue Today", f"${today_revenue:.2f}")
        col4.metric("Avg Sale Value", f"${today_revenue/max(today_sales, 1):.2f}")

        st.write("### Overall Performance")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Sales", total_sales)
        col2.metric("Total Items Sold", total_quantity)
        col3.metric("Total Revenue", f"${total_revenue:.2f}")
        col4.metric("Avg Sale Value", f"${total_revenue/max(total_sales, 1):.2f}")

    def _render_sales_charts(self):
        """Render sales charts and visualizations."""
        # Top products analysis
        st.write("### 🏆 Top Performing Products")

        product_sales = {}
        for sale in self.sales_log:
            product = sale.get("product_name", "Unknown")
            quantity = sale.get("quantity_sold", 0)
            product_sales[product] = product_sales.get(product, 0) + quantity

        if product_sales:
            # Sort by quantity sold
            sorted_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

            # Display top products
            for i, (product, quantity) in enumerate(sorted_products, 1):
                revenue = self._calculate_product_revenue(product)
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"{i}. **{product}**")
                col2.metric("Units Sold", quantity)
                col3.metric("Revenue", f"${revenue:.2f}")

        # Recent sales activity
        st.write("### 📈 Recent Sales Activity")

        # Get last 10 sales
        recent_sales = self.sales_log[-10:] if len(self.sales_log) > 10 else self.sales_log
        recent_sales.reverse()  # Show most recent first

        if recent_sales:
            sales_data = []
            for sale in recent_sales:
                product = sale.get("product_name", "Unknown")
                quantity = sale.get("quantity_sold", 0)
                timestamp = sale.get("timestamp", "Unknown")

                # Find product price
                product_info = next((p for p in self.products if p["name"] == product), {})
                price = product_info.get("price", 0)
                revenue = quantity * price

                sales_data.append({
                    "Time": timestamp.split(" ")[1] if " " in timestamp else timestamp,  # Just time part
                    "Product": product,
                    "Quantity": quantity,
                    "Revenue": f"${revenue:.2f}"
                })

            st.dataframe(sales_data, use_container_width=True)

        # Sales trend (simplified)
        st.write("### 📊 Sales Trend")
        st.info("📈 Advanced trend analysis and forecasting features coming in Phase 3!")

    def _calculate_total_revenue(self):
        """Calculate total revenue from all sales."""
        total = 0
        for sale in self.sales_log:
            product_name = sale.get("product_name")
            quantity = sale.get("quantity_sold", 0)

            # Find product price
            product = next((p for p in self.products if p["name"] == product_name), {})
            price = product.get("price", 0)
            total += quantity * price

        return total

    def _calculate_revenue_for_period(self, filter_func):
        """Calculate revenue for sales matching a filter function."""
        total = 0
        for sale in self.sales_log:
            if filter_func(sale):
                product_name = sale.get("product_name")
                quantity = sale.get("quantity_sold", 0)

                # Find product price
                product = next((p for p in self.products if p["name"] == product_name), {})
                price = product.get("price", 0)
                total += quantity * price

        return total

    def _calculate_product_revenue(self, product_name):
        """Calculate total revenue for a specific product."""
        total = 0
        for sale in self.sales_log:
            if sale.get("product_name") == product_name:
                quantity = sale.get("quantity_sold", 0)

                # Find product price
                product = next((p for p in self.products if p["name"] == product_name), {})
                price = product.get("price", 0)
                total += quantity * price

        return total

    def _is_today(self, timestamp):
        """Check if timestamp is from today (simplified implementation)."""
        # In a real app, this would compare with actual current date
        # For demo purposes, we'll consider all existing sales as "today"
        return True

    def _render_alerts_tab(self):
        """Render the inventory alerts and notifications tab."""
        st.subheader("🚨 Inventory Alerts & Notifications")

        # Get active alerts
        alerts = self._get_active_alerts()

        if not alerts:
            st.success("✅ No active alerts! All systems running smoothly.")
            return

        # Alert summary
        critical_count = len([a for a in alerts if a["severity"] == "critical"])
        warning_count = len([a for a in alerts if a["severity"] == "warning"])
        info_count = len([a for a in alerts if a["severity"] == "info"])

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Alerts", len(alerts))
        col2.metric("Critical", critical_count, delta=f"{'⚠️' if critical_count > 0 else ''}")
        col3.metric("Warnings", warning_count)
        col4.metric("Info", info_count)

        st.divider()

        # Active alerts list
        st.write("### 📋 Active Alerts")

        for alert in alerts:
            self._render_alert_item(alert)

        # Alert history (simplified)
        st.write("### 📚 Recent Alert History")
        st.info("Alert history tracking will be available in Phase 3.")

    def _get_active_alerts(self):
        """Get all active alerts for the employee dashboard."""
        alerts = []

        # Low stock alerts
        low_stock_items = calculate_low_stock(self.products)
        for item in low_stock_items:
            severity = "critical" if item["stock"] <= 2 else "warning"
            alerts.append({
                "id": f"low_stock_{item['name'].lower().replace(' ', '_')}",
                "type": "low_stock",
                "severity": severity,
                "title": f"Low Stock: {item['name']}",
                "message": f"Only {item['stock']} units remaining. Consider restocking soon.",
                "action_required": "Notify Shop Owner",
                "product": item["name"],
                "stock": item["stock"],
                "timestamp": "2026-05-12 09:00:00"  # Would be dynamic in real app
            })

        # Out of stock alerts (critical)
        out_of_stock = [p for p in self.products if p.get("stock", 0) == 0]
        for item in out_of_stock:
            alerts.append({
                "id": f"out_of_stock_{item['name'].lower().replace(' ', '_')}",
                "type": "out_of_stock",
                "severity": "critical",
                "title": f"OUT OF STOCK: {item['name']}",
                "message": f"This item is completely sold out. Immediate restocking required!",
                "action_required": "Urgent: Contact supplier",
                "product": item["name"],
                "stock": 0,
                "timestamp": "2026-05-12 09:00:00"
            })

        # High-selling product alerts (info)
        if self.sales_log:
            product_sales = {}
            for sale in self.sales_log:
                product = sale.get("product_name", "")
                quantity = sale.get("quantity_sold", 0)
                product_sales[product] = product_sales.get(product, 0) + quantity

            # Find products selling fast (arbitrary threshold: >50% of stock sold in recent sales)
            for product_name, sold_quantity in product_sales.items():
                product = next((p for p in self.products if p["name"] == product_name), None)
                if product:
                    total_stock = product.get("stock", 0) + sold_quantity  # Estimate original stock
                    if total_stock > 0 and (sold_quantity / total_stock) > 0.5:
                        alerts.append({
                            "id": f"fast_selling_{product_name.lower().replace(' ', '_')}",
                            "type": "fast_selling",
                            "severity": "info",
                            "title": f"Fast Selling: {product_name}",
                            "message": f"This product is selling quickly. {sold_quantity} units sold recently.",
                            "action_required": "Monitor stock levels",
                            "product": product_name,
                            "sold_recently": sold_quantity,
                            "timestamp": "2026-05-12 09:00:00"
                        })

        return alerts

    def _render_alert_item(self, alert):
        """Render a single alert item with actions."""
        # Color coding based on severity
        if alert["severity"] == "critical":
            icon = "🚨"
            color = "red"
        elif alert["severity"] == "warning":
            icon = "⚠️"
            color = "orange"
        else:
            icon = "ℹ️"
            color = "blue"

        # Alert container
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])

            with col1:
                st.write(f"{icon} **{alert['title']}**")
                st.write(alert["message"])
                st.caption(f"Action Required: {alert['action_required']}")

            with col2:
                # Action buttons based on alert type
                action_key = f"alert_action_{alert['id']}"
                if st.button("Mark Read", key=f"read_{alert['id']}", help="Dismiss this alert"):
                    self._handle_alert_action(alert["id"], "read")
                    st.rerun()

            with col3:
                if alert["type"] in ["low_stock", "out_of_stock"]:
                    if st.button("Report Issue", key=f"report_{alert['id']}", help="Report to management"):
                        self._handle_alert_action(alert["id"], "report")
                        st.success("Issue reported to management!")

            st.divider()

    def _handle_alert_action(self, alert_id, action):
        """Handle alert actions."""
        # In a real app, this would update a database or send notifications
        if "alert_actions" not in st.session_state:
            st.session_state["alert_actions"] = {}

        st.session_state["alert_actions"][alert_id] = {
            "action": action,
            "timestamp": "2026-05-12 09:00:00",  # Would be current time
            "user": "employee"  # Would be current user
        }

        if action == "read":
            st.success("Alert marked as read.")
        elif action == "report":
            st.success("Issue reported to management.")

    def _render_ai_assistant_tab(self):
        """Render a safe fake AI assistant interface for employees."""
        st.subheader("🤖 AI Operations Assistant")
        st.write("Ask Robo about products, stock, inventory, or sales.")

        if "employee_fake_ai_chat_history" not in st.session_state:
            st.session_state["employee_fake_ai_chat_history"] = [
                {
                    "role": "assistant",
                    "content": "Hi! I’m Robo, your Whimsical Sweets assistant. Ask me about products, stock, sales, or inventory."
                }
            ]

        for message in st.session_state["employee_fake_ai_chat_history"]:
            if message["role"] == "user":
                st.markdown(
                    f"""
                    <div style="
                        background-color:#e6f4ff;
                        padding:14px;
                        border-radius:18px;
                        margin:10px 0;
                        max-width:75%;
                        margin-left:auto;
                        border:1px solid #cce7ff;
                    ">
                        <strong>🙋 You</strong><br>
                        {message["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        background-color:#f7f1ff;
                        padding:14px;
                        border-radius:18px;
                        margin:10px 0;
                        max-width:75%;
                        border:1px solid #e4d4ff;
                    ">
                        <strong>🤖 Robo</strong><br>
                        {message["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        with st.form("employee_fake_ai_chat_form", clear_on_submit=True):
            user_question = st.text_input(
                "Ask Robo something:",
                placeholder="Example: What items are low stock?"
            )
            submitted = st.form_submit_button("Send")

        if submitted and user_question:
            st.session_state["employee_fake_ai_chat_history"].append({
                "role": "user",
                "content": user_question
            })

            question = user_question.lower()

            if "low" in question or "restock" in question:
                fake_response = "Demo response: Matcha Cream Puff is currently low on stock and may need restocking soon."
            elif "product" in question or "inventory" in question or "catalog" in question:
                fake_response = "Demo response: The catalog includes cupcakes, pastries, and cookies. You can view full inventory in the Catalog tab."
            elif "sales" in question or "sold" in question:
                fake_response = "Demo response: You can log sales in the Log Sales tab. A future version could summarize recent sales here."
            elif "alert" in question:
                fake_response = "Demo response: You can check the Alerts tab to review low-stock or fast-selling item warnings."
            elif "help" in question:
                fake_response = "Demo response: I can help employees with product lookup, low-stock reminders, sales logging guidance, and alerts."
            else:
                fake_response = "Demo response: This is a safe chatbot interface preview. The real AI connection is turned off for security reasons."

            st.session_state["employee_fake_ai_chat_history"].append({
                "role": "assistant",
                "content": fake_response
            })

            st.rerun()