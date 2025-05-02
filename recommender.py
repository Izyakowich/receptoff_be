import os
import django
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler, MultiLabelBinarizer
from django.utils import timezone
import ast
import logging
import re

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

from recepies.models import CustomUser, Products, Application, ApplicationProducts


class DishRecommender:
    def __init__(self):
        self.dish_features = None
        self.dish_similarity = None
        self.scaler = StandardScaler()
        self.mlb = MultiLabelBinarizer()
        self.df = None
        self.dish_popularity = None
        self.dish_ratings = None
        self.name_mapping = None

    def _clean_name(self, name):
        """Clean dish name for matching"""
        if not isinstance(name, str):
            return ""
        # Remove extra whitespace and convert to lowercase
        return re.sub(r"\s+", " ", name).strip().lower()

    def _create_name_mapping(self):
        """Create mapping between database and CSV dish names"""
        self.name_mapping = {}

        # Clean names in CSV
        self.df["clean_title"] = self.df["title"].apply(self._clean_name)

        # Get all enabled products
        products = Products.objects.filter(status="enabled")

        for product in products:
            clean_name = self._clean_name(product.product_name)
            # Try exact match first
            matches = self.df[self.df["clean_title"] == clean_name]
            if len(matches) > 0:
                self.name_mapping[product.id] = matches.index[0]
                continue

            # Try partial match
            matches = self.df[self.df["clean_title"].str.contains(clean_name, na=False)]
            if len(matches) > 0:
                self.name_mapping[product.id] = matches.index[0]
                continue

            # Try reverse partial match (CSV name contains product name)
            matches = self.df[
                self.df["clean_title"].apply(
                    lambda x: clean_name in x if isinstance(x, str) else False
                )
            ]
            if len(matches) > 0:
                self.name_mapping[product.id] = matches.index[0]

        print(f"Created name mapping for {len(self.name_mapping)} dishes")
        if len(self.name_mapping) == 0:
            print("Warning: No dish mappings found!")
            print("Sample of CSV titles:", self.df["title"].head().tolist())
            print("Sample of product names:", [p.product_name for p in products[:5]])

    def load_data(self):
        """Load and preprocess the EPI-R dataset"""
        try:
            self.df = pd.read_csv("epi_r_updated.csv")
            print(f"Loaded {len(self.df)} dishes from CSV")

            # Convert string lists to actual lists
            categorical_columns = [
                col
                for col in self.df.columns
                if self.df[col].dtype == "object"
                and self.df[col].str.startswith("[").any()
            ]
            for col in categorical_columns:
                self.df[col] = self.df[col].apply(
                    lambda x: ast.literal_eval(x) if pd.notna(x) else []
                )

            # One-hot encode categorical features
            categorical_features = pd.DataFrame()
            for col in categorical_columns:
                encoded = pd.DataFrame(
                    self.mlb.fit_transform(self.df[col]),
                    columns=[f"{col}_{c}" for c in self.mlb.classes_],
                )
                categorical_features = pd.concat(
                    [categorical_features, encoded], axis=1
                )

            # Select numeric features
            numeric_columns = [
                col
                for col in self.df.columns
                if col not in categorical_columns and col not in ["title", "rating"]
            ]
            numeric_features = self.df[numeric_columns].fillna(0)

            # Combine features
            self.dish_features = pd.concat(
                [numeric_features, categorical_features], axis=1
            )
            self.dish_features = self.scaler.fit_transform(self.dish_features)

            # Calculate dish similarity matrix
            self.dish_similarity = cosine_similarity(self.dish_features)
            print(f"Created similarity matrix of shape {self.dish_similarity.shape}")

            # Create name mapping
            self._create_name_mapping()

            # Calculate dish popularity and ratings
            self._calculate_dish_metrics()

        except Exception as e:
            print(f"Error loading data: {e}")
            raise

    def _calculate_dish_metrics(self):
        """Calculate dish popularity and ratings"""
        # Get all approved applications
        applications = Application.objects.filter(status="approved")
        print(f"Found {applications.count()} approved applications")

        # Initialize metrics
        dish_orders = {}
        dish_ratings = {}

        # Count orders and sum ratings for each dish
        for app in applications:
            products = ApplicationProducts.objects.filter(application=app)
            for product in products:
                dish_id = product.products.id
                dish_orders[dish_id] = dish_orders.get(dish_id, 0) + 1
                dish_ratings[dish_id] = (
                    dish_ratings.get(dish_id, 0) + product.products.rating
                )

        # Calculate average ratings
        for dish_id in dish_ratings:
            dish_ratings[dish_id] = dish_ratings[dish_id] / dish_orders[dish_id]

        self.dish_popularity = dish_orders
        self.dish_ratings = dish_ratings
        print(f"Calculated metrics for {len(dish_orders)} dishes")
        print(
            f"Most popular dish has {max(dish_orders.values()) if dish_orders else 0} orders"
        )
        print(
            f"Highest rated dish has rating {max(dish_ratings.values()) if dish_ratings else 0}"
        )

    def get_user_history(self, user_id):
        """Get dishes that user has ordered"""
        applications = Application.objects.filter(id_user_id=user_id, status="approved")
        ordered_dishes = set()

        for app in applications:
            products = ApplicationProducts.objects.filter(application=app)
            for product in products:
                ordered_dishes.add(product.products.id)

        print(f"User {user_id} has ordered {len(ordered_dishes)} dishes")
        return list(ordered_dishes)

    def get_similar_dishes(self, dish_id, n=5):
        """Get n most similar dishes to the given dish"""
        try:
            # Get dish index from mapping
            if dish_id not in self.name_mapping:
                print(f"No mapping found for dish ID {dish_id}")
                return []

            dish_idx = self.name_mapping[dish_id]
            dish_name = self.df.iloc[dish_idx]["title"]
            print(f"Looking for similar dishes to: {dish_name}")

            # Get similar dishes
            similar_dishes = list(enumerate(self.dish_similarity[dish_idx]))
            similar_dishes = sorted(similar_dishes, key=lambda x: x[1], reverse=True)
            similar_dishes = similar_dishes[1 : n + 1]  # Exclude the dish itself

            # Get the dish IDs from the dataframe
            similar_dish_indices = [dish[0] for dish in similar_dishes]
            similar_dish_names = self.df.iloc[similar_dish_indices]["title"].tolist()
            print(f"Found similar dishes: {similar_dish_names}")

            # Find corresponding product IDs in our database
            product_ids = []
            for name in similar_dish_names:
                clean_name = self._clean_name(name)
                try:
                    # Try exact match first
                    product = Products.objects.get(product_name__iexact=clean_name)
                    product_ids.append(product.id)
                    continue
                except Products.DoesNotExist:
                    pass

                try:
                    # Try partial match
                    product = Products.objects.get(product_name__icontains=clean_name)
                    product_ids.append(product.id)
                except Products.DoesNotExist:
                    print(f"Product not found in database: {name}")
                    continue

            print(f"Found {len(product_ids)} matching products in database")
            return product_ids

        except Exception as e:
            print(f"Error finding similar dishes: {e}")
            return []

    def recommend_dishes(
        self,
        user_id,
        n=5,
        similarity_weight=0.6,
        popularity_weight=0.2,
        rating_weight=0.2,
    ):
        """Recommend dishes for a user based on hybrid approach"""
        # Get user's order history
        ordered_dishes = self.get_user_history(user_id)

        # If user has no history, recommend popular and highly rated dishes
        if not ordered_dishes:
            print("No order history found, recommending popular dishes")
            all_dishes = Products.objects.filter(status="enabled")
            print(f"Total enabled dishes: {all_dishes.count()}")

            scored_dishes = []
            max_popularity = (
                max(self.dish_popularity.values()) if self.dish_popularity else 1
            )

            for dish in all_dishes:
                popularity_score = self.dish_popularity.get(dish.id, 0) / max_popularity
                rating_score = (
                    self.dish_ratings.get(dish.id, 0) / 5.0
                )  # Assuming max rating is 5

                # Calculate final score
                final_score = (
                    popularity_weight * popularity_score + rating_weight * rating_score
                )

                scored_dishes.append((dish, final_score))

            # Sort by score and get top n
            scored_dishes.sort(key=lambda x: x[1], reverse=True)
            recommendations = [dish for dish, score in scored_dishes[:n]]
            print(
                f"Generated {len(recommendations)} recommendations based on popularity and rating"
            )
            return recommendations

        # Get similar dishes for each ordered dish
        recommended_dishes = {}
        for dish_id in ordered_dishes:
            similar_dishes = self.get_similar_dishes(dish_id, n)
            for similar_id in similar_dishes:
                if similar_id not in ordered_dishes:
                    # Calculate score for each dish
                    similarity_score = self.dish_similarity[dish_id][similar_id]
                    popularity_score = self.dish_popularity.get(similar_id, 0)
                    rating_score = self.dish_ratings.get(similar_id, 0)

                    # Normalize scores
                    max_popularity = (
                        max(self.dish_popularity.values())
                        if self.dish_popularity
                        else 1
                    )
                    popularity_score = popularity_score / max_popularity
                    rating_score = rating_score / 5.0  # Assuming max rating is 5

                    # Calculate final score
                    final_score = (
                        similarity_weight * similarity_score
                        + popularity_weight * popularity_score
                        + rating_weight * rating_score
                    )

                    recommended_dishes[similar_id] = max(
                        recommended_dishes.get(similar_id, 0), final_score
                    )

        if not recommended_dishes:
            print("No recommendations found based on similar dishes")
            return []

        # Sort dishes by score and get top n
        sorted_dishes = sorted(
            recommended_dishes.items(), key=lambda x: x[1], reverse=True
        )
        top_dish_ids = [dish_id for dish_id, _ in sorted_dishes[:n]]

        # Get dish details
        dishes = Products.objects.filter(id__in=top_dish_ids, status="enabled")
        print(f"Generated {dishes.count()} recommendations based on hybrid approach")
        return dishes


def main():
    recommender = DishRecommender()
    recommender.load_data()

    # Example usage
    user_id = 1  # Replace with actual user ID
    recommendations = recommender.recommend_dishes(user_id)

    print(f"Recommendations for user {user_id}:")
    for dish in recommendations:
        print(
            f"- {dish.product_name} (Score: {recommender.dish_ratings.get(dish.id, 0):.2f})"
        )


if __name__ == "__main__":
    main()
