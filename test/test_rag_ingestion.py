import json

from mockup_sql_ragsetup.ragsetup.dataingestionandload import convertschemattodocument


def test_convertschemattodocument_reads_actual_schema_metadata():
    payload = [
        {
            "id": "tbl_vendor",
            "text_to_embed": "Table: vendor",
            "metadata": {
                "table_name": "vendor",
                "description": "Vendor profile data.",
                "columns": [
                    {"name": "vendor_agreement_number", "type": "VARCHAR(50)", "description": "Agreement id."},
                    {"name": "vendor_name", "type": "VARCHAR(255)", "description": "Vendor name."},
                ],
            },
        },
        {
            "id": "tbl_agreement",
            "text_to_embed": "Table: agreement",
            "metadata": {
                "table_name": "agreement",
                "description": "Agreement data.",
                "columns": [
                    {"name": "agreement_type", "type": "VARCHAR(50)", "description": "Type."},
                ],
            },
        },
    ]

    documents = convertschemattodocument(payload)

    assert len(documents) == 2
    assert "Table Name: vendor" in documents[0].page_content
    assert "vendor_agreement_number" in documents[0].page_content
    assert "Table Name: agreement" in documents[1].page_content
    assert "agreement_type" in documents[1].page_content
