"""
Services package for BusFlow application.

This package contains service classes that handle external integrations
and business logic that spans multiple controllers.

:module: app.services
"""

from app.services.supabase_service import SupabaseService

__all__ = ['SupabaseService']

