def is_in_credal_set(p_hat, pi):
    if len(p_hat.shape) == 1:
        p_hat = p_hat.unsqueeze(0)
    if len(pi.shape) == 1:
        pi = pi.unsqueeze(0)

    c = torch.cumsum(torch.flip(p_hat, dims=[-1]), dim=-1)
    rev_pi = torch.flip(pi, dims=[-1])
    return torch.all(c <= rev_pi, dim=-1)


def gen_lr(p_hat, pi):
    if len(p_hat.shape) < 2:
        p_hat = p_hat.unsqueeze(0)
    if len(pi.shape) < 2:
        pi = pi.unsqueeze(0)

    with torch.no_grad():
        # Sort values
        sorted_pi_rt = pi.sort(descending=True)

        sorted_pi = sorted_pi_rt.values
        sorted_p_hat = torch.gather(p_hat, 1, sorted_pi_rt.indices)

        def search_fn(sorted_p_hat, sorted_pi, sorted_pi_rt_ind):
            result_probs = torch.zeros_like(sorted_p_hat)

            for i in range(sorted_p_hat.shape[0]):
                # Search for loss
                proj = torch.zeros_like(sorted_p_hat[i])

                j = sorted_p_hat[i].shape[0] - 1
                while j >= 0:
                    lookahead = det_lookahead(sorted_p_hat[i], sorted_pi[i], j, proj)
                    proj[lookahead:j + 1] = sorted_p_hat[i][lookahead:j + 1] / torch.sum(
                        sorted_p_hat[i][lookahead:j + 1]) * (
                                                    sorted_pi[i][lookahead] - torch.sum(proj[j + 1:]))

                    j = lookahead - 1

                # e-arrange projection again according to original order
                proj = proj[sorted_pi_rt_ind[i].sort().indices]

                result_probs[i] = proj
            return result_probs

        is_c_set = is_in_credal_set(sorted_p_hat, sorted_pi)

        sorted_p_hat_non_c = sorted_p_hat[~is_c_set]
        sorted_pi_non_c = sorted_pi[~is_c_set]
        sorted_pi_ind_c = sorted_pi_rt.indices[~is_c_set]

        result_probs = torch.zeros_like(sorted_p_hat)
        result_probs[~is_c_set] = search_fn(sorted_p_hat_non_c, sorted_pi_non_c, sorted_pi_ind_c)
        result_probs[is_c_set] = p_hat[is_c_set]

    p_hat = torch.clip(p_hat, 1e-5, 1.)
    result_probs = torch.clip(result_probs, 1e-5, 1.)

    divergence = F.kl_div(p_hat.log(), result_probs, log_target=False, reduction="none")
    divergence = torch.sum(divergence, dim=-1)

    result = torch.where(is_c_set, torch.zeros_like(divergence), divergence)

    return torch.mean(result)


def det_lookahead(p_hat, pi, ref_idx, proj, precision=1e-5):
    for i in range(ref_idx):
        prop = p_hat[i:ref_idx + 1] / torch.sum(p_hat[i:ref_idx + 1])
        prop *= (pi[i] - torch.sum(proj[ref_idx + 1:]))

        # Check violation
        violates = False
        # TODO: Make this more efficient by using cumsum
        for j in range(len(prop)):
            if (torch.sum(prop[j:]) + torch.sum(proj[ref_idx + 1:])) > (torch.max(pi[i + j:]) + precision):
                violates = True
                break

        if not violates:
            return i

    return ref_idx


def construct_p_values(non_conf_scores, preds, non_conf_score_fn):
    num_class = preds.shape[1]
    tmp_non_conf = torch.zeros([preds.shape[0], num_class]).detach()
    p_values = torch.zeros([preds.shape[0], num_class]).detach()
    for clz in range(num_class):
        tmp_non_conf[:, clz] = non_conf_score_fn(preds, torch.tensor(clz).repeat(preds.shape[0]))
        p_values[:, clz] = p_value(non_conf_scores, tmp_non_conf[:, clz])
    return p_values


def non_conformity_score_prop(predictions, targets) -> torch.Tensor:
    if len(predictions.shape) == 1:
        predictions = predictions.unsqueeze(0)
    if len(targets.shape) == 1:
        targets = targets.unsqueeze(1)

    class_val = torch.gather(predictions, 1, targets.type(torch.int64))
    num_class = predictions.shape[1]

    # Exclude the target class here
    indices = torch.arange(0, num_class).view(1, -1).repeat(predictions.shape[0], 1)
    mask = torch.zeros_like(indices).bool()
    mask.scatter_(1, targets.type(torch.int64), True)

    selected_predictions = predictions[~mask].view(-1, args.num_classes - 1)

    return torch.max(selected_predictions, dim=-1).values.squeeze() / (
            class_val.squeeze() + args.non_conf_score_prop_gamma + 1e-5)


def non_conformity_score_diff(predictions, targets) -> torch.Tensor:
    if len(predictions.shape) == 1:
        predictions = predictions.unsqueeze(0)
    if len(targets.shape) == 1:
        targets = targets.unsqueeze(1)
    num_class = predictions.shape[1]
    class_val = torch.gather(predictions, 1, targets.type(torch.int64))

    # Exclude the target class here
    indices = torch.arange(0, num_class).view(1, -1).repeat(predictions.shape[0], 1)
    mask = torch.zeros_like(indices).bool()
    mask.scatter_(1, targets.type(torch.int64), True)

    selected_predictions = predictions[~mask].view(-1, num_class - 1)

    return torch.max(selected_predictions - class_val, dim=-1).values

