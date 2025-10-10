import { Router } from "express";
import { saveArticle, getSavedArticles, deleteSavedArticle } from "../controllers/savedArticleController.js";
import authMiddleware from "../middlewares/auth.js";

const savedArticleRouter = Router();

savedArticleRouter.post('/:userId', authMiddleware, saveArticle);
savedArticleRouter.get('/:userId',  getSavedArticles);
savedArticleRouter.delete('/:userId', authMiddleware, deleteSavedArticle);

export default savedArticleRouter;