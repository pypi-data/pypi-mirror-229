from fastapi import Request, Response
from fastapi.routing import APIRoute
from fastsession import FastSessionMiddleware, MemoryStore
from starlette.middleware.cors import CORSMiddleware

from .access_control.default_client_role_grant_middleware import DefaultClientRoleGrantMiddleware
from .default_api_names import DefaultApiNames
from .default_api_names_to_path import to_web_api_path


def append_middlewares(chat_stream, app, logger, eloc, opts=None, ):
    """
    ChatStreamに関連する Middleware を FastAPI アプリ に 追加する。
    """

    if opts is None:
        opts = {
            "fast_session": {
                "secret_key": "chatstream-default-session-secret-key",
                "store": MemoryStore(),
            },
            "develop_mode": False,
            "cors": {
                "allow_origins": ["*"]
            }
        }

    app.add_middleware(DefaultClientRoleGrantMiddleware, chat_stream=chat_stream)

    logger.debug(eloc.to_str({
        "en": f"Middleware for granting default roles has been added.",
        "ja": f"デフォルトロール付与用ミドルウェア を追加しました。"}))

    fast_session_opts = opts.get("fast_session")
    store = MemoryStore()

    same_site = None
    if fast_session_opts is not None:
        store = fast_session_opts.get("store", MemoryStore())
        same_site = fast_session_opts.get("same_site", None)

    is_http_only = True
    is_secure = True

    logger.debug(eloc.to_str({
        "en": f"Middleware for HTTP sessions (FastSession) with same_site:{same_site} http_only:{is_http_only} secure:{is_secure}",
        "ja": f"HTTPセッション用ミドルウェアの設定 same_site:{same_site} http_only:{is_http_only} secure:{is_secure}"}))
    app.add_middleware(FastSessionMiddleware,
                       secret_key="your-session-secret-key",  # Key for cookie signature
                       store=store,  # Store for session saving
                       same_site=same_site,
                       http_only=is_http_only,  # True: Cookie cannot be accessed from client-side scripts such as JavaScript
                       # secure属性について
                       # secure 属性は常に True とする。
                       # secure:True でもローカルホストで開発する場合は https は免除される(chrome)。
                       # また、ローカルホスト開発においてフロントエンドとChatStreamサーバーのホストが異なる場合（=ローカルホスト内でのクロスオリジン）、
                       # same_site:"None" を指定する必要があるが、secure属性が False の場合、 same_site:"None" は無視されるため
                       # セッションクッキーは機能せずクロスオリジンに期待された動作をすることはできないので、多くのシチュエーションで secure=True の運用が好ましい。
                       secure=True,
                       skip_session_header={"header_name": "X-FastSession-Skip", "header_value": "skip"},
                       logger=chat_stream.logger
                       )

    logger.debug(eloc.to_str({
        "en": f"Middleware for HTTP sessions (FastSession) is added.",
        "ja": f"HTTPセッション用ミドルウェア(FastSession) を追加しました。"}))

    cors_opts = opts.get("cors", None)
    if cors_opts is not None:
        allow_origins = cors_opts.get("allow_origins", ["*"])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=[
                "X-ChatStream-API-DevTool-Enabled",  # UI側で開発ツール(DevTool) を有効にできるか否かを示すフラグ
                "X-ChatStream-Last-Generated-Message-Id",  # 直前に生成された最新メッセージのメッセージID
            ],
        )

        logger.warning(eloc.to_str({
            "en": f"CORS middleware has been added. As a development mode, all origins, methods, and headers are now acceptable. Please note that if you see this log in production, there is a security issue.",
            "ja": f"CORSミドルウェアを追加しました。開発モードとして、すべてのオリジン、メソッド、ヘッダが受け入れが可能となっています。プロダクションでこのログが表示された場合はセキュリティ上の問題がありますので注意してください。"}))

        logger.debug(eloc.to_str({
            "en": f"CORS middleware's allow_origins is {allow_origins}",
            "ja": f"CORSミドルウェアの allow_origins の設定は {allow_origins}です。"
                  f"開発モードでフロントエンドとサーバーのドメインが異なるクロスドメインアクセスするをするとき、"
                  f"credential(セッションクッキーなど)が include に設定してアクセスする場合[*]の場合はCORSポリシー違反となる場合があるため、"
                  f"allow_originsには具体的なホスト名('http://localhost:xxxx') を指定してください。"}))
