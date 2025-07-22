PostFiat Python SDK Documentation
=================================

Welcome to the PostFiat Python SDK documentation.

The PostFiat SDK is a proto-first, multi-language SDK for building applications with the PostFiat protocol.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api/index

Getting Started
===============

The PostFiat SDK provides Python classes and utilities for:

- **Protocol Buffer Messages**: Auto-generated classes for all PostFiat message types
- **Envelope Management**: Tools for creating, storing, and retrieving encrypted message envelopes
- **Client Services**: High-level client interfaces for interacting with PostFiat services
- **Type Safety**: Pydantic models and type definitions for robust development

Installation
============

.. code-block:: bash

   pip install postfiat-sdk

Basic Usage
===========

.. code-block:: python

   from postfiat import PostFiatClient
   
   # Create a client
   client = PostFiatClient()
   
   # Use the SDK
   # ... (documentation for basic usage)

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`