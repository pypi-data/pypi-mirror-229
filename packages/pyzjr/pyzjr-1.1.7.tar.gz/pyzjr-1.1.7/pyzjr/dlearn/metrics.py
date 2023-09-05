# Dice系数 Dice Loss
import torch

def Dice_coeff(pred, true, reduce_batch_first=False, epsilon=1e-6):
    """
    二分类，计算预测和目标的Dice系数的平均值
    :param pred: Tensor，预测的分割结果
    :param true: Tensor，真实的分割标签
    :param reduce_batch_first: bool，是否在批次维度上求平均，如果希望在整个批次上获得一个总体的Dice系数，
                               可以设置为 False。如果希望获得每个样本的Dice系数，并根据需要进行进一步的
                               处理，可以设置为 True。
    :param epsilon: float，平滑因子，避免分母为零
    :return: Tensor，Dice系数的平均值
    """
    assert pred.size() == true.size()
    assert pred.dim() == 3 or not reduce_batch_first

    if pred.dim() == 2 or not reduce_batch_first:
        sum_dim = (-1, -2)
    else:
        sum_dim=(-1, -2, -3)

    inter = 2 * (pred * true).sum(dim=sum_dim)
    sets_sum = pred.sum(dim=sum_dim) + true.sum(dim=sum_dim)
    sets_sum = torch.where(sets_sum == 0, inter, sets_sum)

    dice = (inter + epsilon) / (sets_sum + epsilon)
    return dice.mean()


def multiclass_Dice_coeff(pred, true, reduce_batch_first=False, epsilon=1e-6):
    """
    计算多类别分割任务中所有类别的Dice系数的平均值
    :param pred: Tensor，预测的分割结果
    :param true: Tensor，真实的分割标签
    :param reduce_batch_first: bool，是否在批次维度上求平均
    :param epsilon: float，平滑因子，避免分母为零
    :return: Tensor，所有类别的Dice系数的平均值
    """
    return Dice_coeff(pred.flatten(0, 1), true.flatten(0, 1), reduce_batch_first, epsilon)


def Dice_Loss(pred, true, multiclass=False):
    """
    计算Dice损失（目标是最小化），介于0和1之间
    :param pred: Tensor，预测的分割结果
    :param true: Tensor，真实的分割标签
    :param multiclass: bool，是否为多类别分割任务
    :return: Tensor，Dice损失
    """
    diceloss = multiclass_Dice_coeff if multiclass else Dice_coeff
    return 1 - diceloss(pred, true, reduce_batch_first=True)
