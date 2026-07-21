import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-open-synergy-ssi-vendor-bill",
    description="Meta package for open-synergy-ssi-vendor-bill Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-ssi_vendor_bill',
        'odoo14-addon-ssi_vendor_bill_claude_code',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
