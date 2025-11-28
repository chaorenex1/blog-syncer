import datetime

from sqlalchemy import Column, DateTime, Integer, String, text, UUID, Index, func, TEXT

from models import Base


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_document"
    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"), comment="id")
    knowledge_base_id = Column(UUID(as_uuid=True), index=True, nullable=False, comment="knowledge_base_id")
    created_at = Column(DateTime, default=datetime.datetime.now(), comment="create time")
    updated_at = Column(DateTime, default=datetime.datetime.now(), comment="update time")
    deleted = Column(Integer, default=0, comment="delete flag")
    title = Column(String(255), nullable=False, comment="name")
    file_id = Column(String, index=True, nullable=True, comment="file id")
    message_id = Column(String, index=True, nullable=True, comment="message id")
    content = Column(TEXT, nullable=False, comment="content", server_default=text("''"))
    doc_language = Column(String(50), nullable=False, comment="knowledge language")
    doc_from = Column(String(255), nullable=True, comment="document from", server_default=text("''"))
    rag_type = Column(String, index=True, nullable=False, comment="rag type")
    data_source_type = Column(String, index=True, nullable=False, comment="data source type")
    rag_status = Column(String(50), nullable=True, comment="rag status")
    error_message = Column(String(255), nullable=True, comment="error message", server_default=text("''"))
    stop_at = Column(DateTime, nullable=True, comment="stop at")
    word_count = Column(Integer, nullable=True, server_default=text("0"), comment="word count")
    extracted_at = Column(DateTime, nullable=True, comment="extracted at")
    spited_at = Column(DateTime, nullable=True, comment="split at")
    cleaned_at = Column(DateTime, nullable=True, comment="cleaned at")
    indexed_at = Column(DateTime, nullable=True, comment="embedded at")
    indexed_time = Column(Integer, nullable=True, server_default=text("0"), comment="indexed times")
    token_count = Column(Integer, nullable=True, server_default=text("0"), comment="token count")
    push_status = Column(Integer, nullable=True, server_default=text("0"), comment="push status")
    push_time = Column(DateTime, nullable=True, comment="push time")

    __table_args__ = (
        Index("idx_knowledge_document_content", func.to_tsvector(text("'jieba_cfg'"), content), postgresql_using="gin"),
    )